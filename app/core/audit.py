from contextvars import ContextVar, Token
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from sqlalchemy import event, inspect as sqlalchemy_inspect
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.base import BaseModel


_audit_context: ContextVar[dict[str, Any]] = ContextVar(
    "audit_context",
    default={},
)
_listeners_registered = False
_SENSITIVE_FIELDS = {"hashed_password", "password", "secret_key"}


def set_audit_context(**values: Any) -> Token:
    return _audit_context.set(values)


def reset_audit_context(token: Token) -> None:
    _audit_context.reset(token)


def _json_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bytes):
        return f"<{len(value)} bytes>"
    return value


def _snapshot(instance: object) -> dict[str, Any]:
    mapper = sqlalchemy_inspect(instance).mapper
    return {
        attribute.key: _json_value(getattr(instance, attribute.key))
        for attribute in mapper.column_attrs
        if attribute.key not in _SENSITIVE_FIELDS
    }


def _changed_values(instance: object) -> tuple[dict[str, Any], dict[str, Any]]:
    state = sqlalchemy_inspect(instance)
    old_values: dict[str, Any] = {}
    new_values: dict[str, Any] = {}
    for attribute in state.mapper.column_attrs:
        key = attribute.key
        if key in _SENSITIVE_FIELDS:
            continue
        history = state.attrs[key].history
        if not history.has_changes():
            continue
        old_values[key] = _json_value(history.deleted[0]) if history.deleted else None
        new_values[key] = _json_value(getattr(instance, key))
    return old_values, new_values


def _apply_actor_fields(session: Session) -> None:
    context = _audit_context.get()
    username = context.get("username")
    now = datetime.utcnow()

    for instance in session.new:
        if isinstance(instance, BaseModel) and username and not instance.created_by:
            instance.created_by = username

    for instance in session.dirty:
        if not isinstance(instance, BaseModel):
            continue
        if username:
            instance.updated_by = username
        state = sqlalchemy_inspect(instance)
        deleted_history = state.attrs.is_deleted.history
        if (
            deleted_history.has_changes()
            and instance.is_deleted
            and not instance.deleted_at
        ):
            instance.deleted_at = now
            instance.deleted_by = username


def _before_flush(session: Session, flush_context: object, instances: object) -> None:
    if session.info.get("audit_disabled"):
        return

    _apply_actor_fields(session)
    changes: list[dict[str, Any]] = []

    for instance in session.new:
        if isinstance(instance, AuditLog):
            continue
        if hasattr(instance, "__table__"):
            changes.append(
                {
                    "instance": instance,
                    "operation": "CREATE",
                    "old_values": None,
                    "new_values": None,
                }
            )

    for instance in session.dirty:
        if isinstance(instance, AuditLog) or not session.is_modified(
            instance,
            include_collections=False,
        ):
            continue
        old_values, new_values = _changed_values(instance)
        if not new_values:
            continue
        operation = (
            "SOFT_DELETE"
            if new_values.get("is_deleted") is True
            else "UPDATE"
        )
        changes.append(
            {
                "instance": instance,
                "operation": operation,
                "old_values": old_values,
                "new_values": new_values,
            }
        )

    for instance in session.deleted:
        if isinstance(instance, AuditLog):
            continue
        if hasattr(instance, "__table__"):
            changes.append(
                {
                    "instance": instance,
                    "operation": "DELETE",
                    "old_values": _snapshot(instance),
                    "new_values": None,
                }
            )

    if changes:
        session.info.setdefault("audit_changes", []).extend(changes)


def _after_flush_postexec(session: Session, flush_context: object) -> None:
    changes = session.info.pop("audit_changes", [])
    if not changes:
        return

    context = _audit_context.get()
    rows = []
    for change in changes:
        instance = change["instance"]
        record_id = getattr(instance, "id", None)
        if record_id is None:
            continue
        rows.append(
            {
                "user_id": context.get("user_id"),
                "username": context.get("username") or "system",
                "ip_address": context.get("ip_address"),
                "table_name": instance.__table__.name,
                "record_id": record_id,
                "operation": change["operation"],
                "old_values": change["old_values"],
                "new_values": (
                    _snapshot(instance)
                    if change["operation"] == "CREATE"
                    else change["new_values"]
                ),
                "module": instance.__class__.__module__.rsplit(".", 1)[-1],
            }
        )

    if rows:
        session.connection().execute(AuditLog.__table__.insert(), rows)


def register_audit_listeners() -> None:
    global _listeners_registered
    if _listeners_registered:
        return
    event.listen(Session, "before_flush", _before_flush)
    event.listen(Session, "after_flush_postexec", _after_flush_postexec)
    _listeners_registered = True
