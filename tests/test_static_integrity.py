import ast
from pathlib import Path


def iter_python_files():
    for path in Path("app").rglob("*.py"):
        if "__pycache__" not in path.parts:
            yield path
    yield Path("main.py")
    yield Path("test_db.py")


def test_python_files_parse():
    for path in iter_python_files():
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))


def test_template_response_references_exist():
    missing = []
    for path in Path("app/routers").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "TemplateResponse"
                and node.args
                and isinstance(node.args[0], ast.Constant)
            ):
                template_name = node.args[0].value
                if not (Path("app/templates") / template_name).exists():
                    missing.append(f"{path}: {template_name}")
    assert missing == []


def get_router_paths(path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    routes = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Attribute)
                    and decorator.func.attr in {"get", "post", "put", "delete", "patch"}
                    and decorator.args
                    and isinstance(decorator.args[0], ast.Constant)
                ):
                    routes.append((decorator.func.attr.upper(), decorator.args[0].value, node.name))
    return routes


def test_pages_router_has_no_duplicate_routes():
    routes = get_router_paths(Path("app/routers/pages.py"))
    seen = {}
    duplicates = []
    for method, route_path, name in routes:
        key = (method, route_path)
        if key in seen:
            duplicates.append(f"{method} {route_path}: {seen[key]} / {name}")
        else:
            seen[key] = name
    assert duplicates == []


def test_no_legacy_pages_router_copy():
    assert not Path("app/routers/pages1.py").exists()
