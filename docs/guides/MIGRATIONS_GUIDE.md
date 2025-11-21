# Database Migrations Guide

Complete guide to managing database schema changes using Alembic in the standmate-be project.

## Table of Contents

- [What Are Migrations?](#what-are-migrations)
- [Setup Alembic](#setup-alembic)
- [Common Migration Workflows](#common-migration-workflows)
- [Migration Commands Reference](#migration-commands-reference)
- [Best Practices](#best-practices)

## What Are Migrations?

**Migrations** are version-controlled database schema changes. They allow you to:

- Track all database schema changes over time
- Apply changes consistently across environments (dev, staging, production)
- Roll back changes if something goes wrong
- Collaborate with team members without conflicts

### The Problem Migrations Solve

**Without migrations:**
```python
# You update your model
class Task(Base):
    title: Mapped[str] = mapped_column(String(200))
    priority: Mapped[int] = mapped_column(Integer)  # NEW FIELD

# Now what? How do you update the database?
# Manual SQL? What about production? What about teammates?
```

**With migrations:**
```bash
# Alembic detects the change and creates a migration script
alembic revision --autogenerate -m "add priority to tasks"

# Apply to database
alembic upgrade head

# Done! Database is updated, change is tracked in version control
```

## Setup Alembic

### Step 1: Install Alembic

```bash
pip install alembic
```

### Step 2: Initialize Alembic

Run this command from your project root (`/Users/gnirmalkumar/Documents/work/standmate-be`):

```bash
alembic init alembic
```

This creates:
```
standmate-be/
├── alembic/              # Migration scripts directory
│   ├── versions/         # Individual migration files go here
│   ├── env.py           # Alembic environment configuration
│   └── script.py.mako   # Template for new migrations
└── alembic.ini          # Alembic configuration file
```

### Step 3: Configure Alembic

#### 3a. Update `alembic.ini`

Find this line in `alembic.ini`:
```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

**Replace it with:**
```ini
# Leave this commented out - we'll set it in env.py instead
# sqlalchemy.url = 
```

#### 3b. Update `alembic/env.py`

Replace the entire `alembic/env.py` file with this configuration:

```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Import your Base and all models
import sys
from pathlib import Path
import importlib
import pkgutil

# Add the app directory to the path
app_path = Path(__file__).resolve().parents[1] / "app"
sys.path.append(str(app_path))

# Import Base first
from models.task import Base
from core.config import settings

# Automatically import all models from the models directory
models_path = app_path / "models"
if models_path.exists():
    for (_, module_name, _) in pkgutil.iter_modules([str(models_path)]):
        # Skip __init__ and import all other modules
        if module_name != "__init__":
            importlib.import_module(f"models.{module_name}")

# this is the Alembic Config object
config = context.config

# Set the database URL from your settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async support."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

> [!TIP]
> **Automatic Model Discovery**: The configuration above automatically imports all models from the `models/` directory. When you create a new model file (e.g., `user.py`), it will be automatically detected—no need to manually update `env.py`!

### Step 4: Create Your First Migration

```bash
# Generate initial migration (creates tables)
alembic revision --autogenerate -m "initial migration"

# Apply the migration
alembic upgrade head
```

## Common Migration Workflows

### 1. Adding a New Field to Existing Model

**Scenario:** Add a `priority` field to the `Task` model

```python
# app/models/task.py
class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    priority: Mapped[int] = mapped_column(Integer, default=1)  # NEW FIELD
```

**Generate and apply migration:**
```bash
alembic revision --autogenerate -m "add priority to tasks"
alembic upgrade head
```

### 2. Creating a New Model/Table

**Scenario:** Create a new `User` model

```python
# app/models/user.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from models.task import Base  # Import Base from existing model

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
```

**Generate and apply migration:**
```bash
# No need to update env.py - models are auto-imported!
alembic revision --autogenerate -m "create users table"
alembic upgrade head
```

### 3. Adding a Relationship (Foreign Key)

**Scenario:** Add `user_id` to `Task` to link tasks to users

```python
# app/models/task.py
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))  # NEW
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="tasks")
```

**Generate and apply migration:**
```bash
alembic revision --autogenerate -m "add user relationship to tasks"
alembic upgrade head
```

### 4. Renaming a Column

**Scenario:** Rename `description` to `details`

Alembic might not detect renames automatically. You may need to edit the migration:

```bash
alembic revision -m "rename description to details"
```

Edit the generated migration file in `alembic/versions/`:
```python
def upgrade() -> None:
    op.alter_column('tasks', 'description', new_column_name='details')

def downgrade() -> None:
    op.alter_column('tasks', 'details', new_column_name='description')
```

Then apply:
```bash
alembic upgrade head
```

### 5. Rolling Back a Migration

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

## Migration Commands Reference

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration (for manual edits)
alembic revision -m "description"
```

### Applying Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply next migration
alembic upgrade +1

# Apply to specific revision
alembic upgrade <revision_id>
```

### Rolling Back

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all
alembic downgrade base
```

### Checking Status

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --verbose
```

## Best Practices

### 1. Always Review Auto-Generated Migrations

After running `alembic revision --autogenerate`, **always check** the generated file in `alembic/versions/`:

```python
# alembic/versions/xxxx_add_priority.py
def upgrade() -> None:
    # Review these operations!
    op.add_column('tasks', sa.Column('priority', sa.Integer(), nullable=True))

def downgrade() -> None:
    # Make sure rollback works!
    op.drop_column('tasks', 'priority')
```

### 2. Use Descriptive Migration Messages

```bash
# Good
alembic revision --autogenerate -m "add priority and due_date to tasks"

# Bad
alembic revision --autogenerate -m "update"
```

### 3. Test Migrations Before Production

```bash
# Apply migration
alembic upgrade head

# Test your application

# If there's an issue, rollback
alembic downgrade -1
```

### 4. Never Edit Applied Migrations

Once a migration is applied (especially in production), **never edit it**. Instead, create a new migration to fix issues.

### 5. Commit Migrations to Version Control

```bash
git add alembic/versions/
git commit -m "Add migration: add priority to tasks"
```

### 6. Handle Data Migrations Carefully

For complex data transformations, use manual migrations:

```python
# alembic/versions/xxxx_migrate_data.py
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Add new column
    op.add_column('tasks', sa.Column('priority', sa.Integer(), nullable=True))
    
    # Migrate data
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE tasks SET priority = 1 WHERE status = 'pending'")
    )
    connection.execute(
        sa.text("UPDATE tasks SET priority = 2 WHERE status = 'in_progress'")
    )
    
    # Make column non-nullable
    op.alter_column('tasks', 'priority', nullable=False)
```

### 7. Keep Models and Migrations in Sync

Your models should always match your database schema. If they don't:

```bash
# Generate migration to sync them
alembic revision --autogenerate -m "sync models with database"
```

## Workflow Summary

### Daily Development Workflow

1. **Modify your models** (add/change fields)
2. **Generate migration:** `alembic revision --autogenerate -m "description"`
3. **Review the migration** in `alembic/versions/`
4. **Apply migration:** `alembic upgrade head`
5. **Test your changes**
6. **Commit to git:** `git add alembic/versions/ && git commit -m "..."`

### Deploying to Production

1. **Pull latest code** (includes new migrations)
2. **Apply migrations:** `alembic upgrade head`
3. **Restart application**

## Troubleshooting

### "Target database is not up to date"

```bash
# Check current version
alembic current

# Apply pending migrations
alembic upgrade head
```

### "Can't locate revision identified by 'xxxx'"

The migration file might be missing. Check `alembic/versions/` directory.

### "Multiple head revisions are present"

You have branching migrations. Merge them:
```bash
alembic merge heads -m "merge migrations"
```

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQLAlchemy Migrations](https://docs.sqlalchemy.org/en/20/core/metadata.html#altering-database-objects-through-migrations)
