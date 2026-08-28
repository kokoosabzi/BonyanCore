from pathlib import Path


def test_requirements_file_declares_runtime_dependencies():
    requirements = Path("requirements.txt").read_text(encoding="utf-8-sig")
    for package in ("fastapi", "sqlalchemy", "pydantic", "jdatetime"):
        assert package in requirements
