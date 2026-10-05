"""Enforces the dependency rule: inner layers never import frameworks or outer layers."""

import ast
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "src" / "editalmind_ai"

FRAMEWORKS = {
    "fastapi",
    "starlette",
    "sqlalchemy",
    "alembic",
    "beanie",
    "motor",
    "pymongo",
    "redis",
    "celery",
    "boto3",
    "httpx",
    "anthropic",
    "openai",
    "pydantic_settings",
}

FORBIDDEN_IMPORTS = {
    "domain": FRAMEWORKS
    | {"editalmind_ai.application", "editalmind_ai.infrastructure", "editalmind_ai.presentation"},
    "application": FRAMEWORKS | {"editalmind_ai.infrastructure", "editalmind_ai.presentation"},
}


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            modules.add(node.module)
    return modules


def violations(module: str, forbidden: set[str]) -> bool:
    return any(module == name or module.startswith(f"{name}.") for name in forbidden)


@pytest.mark.parametrize("layer", sorted(FORBIDDEN_IMPORTS))
def test_layer_respects_dependency_rule(layer: str) -> None:
    forbidden = FORBIDDEN_IMPORTS[layer]
    offenders = [
        f"{path.relative_to(PACKAGE_ROOT)} imports {module}"
        for path in sorted((PACKAGE_ROOT / layer).rglob("*.py"))
        for module in imported_modules(path)
        if violations(module, forbidden)
    ]

    assert offenders == []


def test_detects_forbidden_import(tmp_path: Path) -> None:
    source = tmp_path / "bad.py"
    source.write_text("from fastapi import APIRouter\nimport editalmind_ai.infrastructure.db\n")

    modules = imported_modules(source)

    assert violations("fastapi", FORBIDDEN_IMPORTS["domain"])
    assert {"fastapi", "editalmind_ai.infrastructure.db"} <= modules
    assert violations("editalmind_ai.infrastructure.db", FORBIDDEN_IMPORTS["application"])
    assert not violations("pydantic", FORBIDDEN_IMPORTS["domain"])
