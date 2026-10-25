"""Script to scaffold a new domain module in src/app/modules/.

Usage:
    python scripts/create_module.py <module_name> [--force]

Example:
    python scripts/create_module.py category
    python scripts/create_module.py tag
    python scripts/create_module.py comment
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = PROJECT_ROOT / "src" / "app" / "modules"


def to_pascal_case(snake_str: str) -> str:
    """Convert snake_case to PascalCase (e.g. blog_post -> BlogPost)."""
    return "".join(part.capitalize() for part in snake_str.split("_"))


def to_plural(word: str) -> str:
    """Simple pluralizer for English words."""
    if word.endswith("y") and not word.endswith(("ay", "ey", "oy", "uy")):
        return word[:-1] + "ies"
    if word.endswith(("s", "sh", "ch", "x", "z")):
        return word + "es"
    return word + "s"


def get_init_template(class_name: str) -> str:
    return f'"""{class_name} domain module."""\n'


def get_models_template(class_name: str, table_name: str) -> str:
    return f"""from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class {class_name}(Base):
    __tablename__ = "{table_name}"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
"""


def get_schemas_template(class_name: str) -> str:
    return f"""from pydantic import BaseModel, ConfigDict


class {class_name}Base(BaseModel):
    pass


class {class_name}Create({class_name}Base):
    pass


class {class_name}Update({class_name}Base):
    pass


class {class_name}Read({class_name}Base):
    id: int

    model_config = ConfigDict(from_attributes=True)
"""


def get_repository_template(class_name: str, module_name: str) -> str:
    return f"""from sqlalchemy.orm import Session

from app.modules.{module_name}.models import {class_name}  # noqa: F401


class {class_name}Repository:
    def __init__(self, session: Session) -> None:
        self.session = session
"""


def get_service_template(class_name: str, module_name: str) -> str:
    return f"""from sqlalchemy.orm import Session

from app.modules.{module_name}.repository import {class_name}Repository


class {class_name}Service:
    def __init__(self, session: Session) -> None:
        self.repository = {class_name}Repository(session)
"""


def get_router_template(class_name: str, module_name: str) -> str:
    return f"""from fastapi import APIRouter

from app.api.deps import DatabaseSession  # noqa: F401
from app.modules.{module_name}.service import {class_name}Service  # noqa: F401

router = APIRouter()
"""


def create_module(name: str, force: bool = False) -> None:
    # Clean and validate module name
    module_name = name.strip().lower()
    if not re.match(r"^[a-z][a-z0-9_]*$", module_name):
        print(f"[Error] Invalid module name '{name}'. Must be a valid snake_case identifier.")
        sys.exit(1)

    target_dir = MODULES_DIR / module_name
    if target_dir.exists() and not force:
        print(f"[Error] Module directory '{target_dir}' already exists. Use --force to overwrite.")
        sys.exit(1)

    class_name = to_pascal_case(module_name)
    plural_name = to_plural(module_name)
    table_name = plural_name

    target_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "__init__.py": get_init_template(class_name),
        "models.py": get_models_template(class_name, table_name),
        "schemas.py": get_schemas_template(class_name),
        "repository.py": get_repository_template(class_name, module_name),
        "service.py": get_service_template(class_name, module_name),
        "router.py": get_router_template(class_name, module_name),
    }

    for filename, content in files.items():
        file_path = target_dir / filename
        file_path.write_text(content, encoding="utf-8")
        print(f"  + Created {file_path.relative_to(PROJECT_ROOT)}")

    print(f"\n[Success] Simple template for module '{module_name}' created in {target_dir.relative_to(PROJECT_ROOT)}!")
    print("\nNext Steps:")
    print("1. Register the router in 'src/app/api/v1.py':")
    print(f"   from app.modules.{module_name}.router import router as {module_name}_router")
    print(f'   router.include_router({module_name}_router, prefix="/{plural_name}", tags=["{plural_name.capitalize()}"])')
    print("\n2. Include the model in 'alembic/env.py':")
    print(f"   from app.modules.{module_name} import models as {module_name}_models  # noqa: F401")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a simple domain module template in FastAPI Blog.")
    parser.add_argument("name", help="Name of the module (e.g. category, tag, comment)")
    parser.add_argument("-f", "--force", action="store_true", help="Overwrite existing module files if directory exists")
    args = parser.parse_args()
    create_module(args.name, force=args.force)


if __name__ == "__main__":
    main()
