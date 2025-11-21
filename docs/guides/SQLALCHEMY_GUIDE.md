# SQLAlchemy ORM Guide

Complete guide to using SQLAlchemy 2.0 with async support in the standmate-be project.

## Table of Contents

- [Overview](#overview)
- [Defining Models](#defining-models)
- [CRUD Operations](#crud-operations)
- [Querying Data](#querying-data)
- [Relationships](#relationships)
- [Advanced Queries](#advanced-queries)
- [Best Practices](#best-practices)

## Overview

This project uses **SQLAlchemy 2.0** with async support:
- **ORM**: SQLAlchemy 2.0 with declarative base
- **Database Driver**: asyncpg (PostgreSQL)
- **Session Type**: AsyncSession
- **Style**: Modern type-annotated models

## Defining Models

### Basic Model Structure

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Text, DateTime, Boolean
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "tasks"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Required fields
    title: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    
    # Optional fields (use | None)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Boolean fields
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
```

### Common Column Types

```python
from sqlalchemy import String, Integer, Text, DateTime, Boolean, Float, JSON

# String with max length
name: Mapped[str] = mapped_column(String(100))

# Integer
count: Mapped[int] = mapped_column(Integer)

# Text (unlimited length)
content: Mapped[str] = mapped_column(Text())

# DateTime
created_at: Mapped[datetime] = mapped_column(DateTime)

# Boolean
is_active: Mapped[bool] = mapped_column(Boolean, default=True)

# Float
price: Mapped[float] = mapped_column(Float)

# JSON
metadata: Mapped[dict] = mapped_column(JSON)
```

## CRUD Operations

### Create (Insert)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from models.task import Task

async def create_task(db: AsyncSession, title: str, description: str = None):
    # Create new instance
    task = Task(
        title=title,
        description=description,
        status="pending"
    )
    
    # Add to session
    db.add(task)
    
    # Commit to database
    await db.commit()
    
    # Refresh to get generated fields (like id)
    await db.refresh(task)
    
    return task
```

**Usage in FastAPI route:**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str | None = None

@router.post("/tasks")
async def create_task_endpoint(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    task = Task(**task_data.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task
```

### Read (Query)

```python
from sqlalchemy import select

# Get all tasks
async def get_all_tasks(db: AsyncSession):
    result = await db.execute(select(Task))
    tasks = result.scalars().all()
    return tasks

# Get single task by ID
async def get_task_by_id(db: AsyncSession, task_id: int):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    return task

# Get with filter
async def get_pending_tasks(db: AsyncSession):
    result = await db.execute(
        select(Task).where(Task.status == "pending")
    )
    tasks = result.scalars().all()
    return tasks
```

**FastAPI route example:**

```python
@router.get("/tasks")
async def list_tasks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task))
    tasks = result.scalars().all()
    return tasks

@router.get("/tasks/{task_id}")
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

### Update

```python
# Method 1: Fetch, modify, commit
async def update_task(db: AsyncSession, task_id: int, title: str = None, status: str = None):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        return None
    
    if title:
        task.title = title
    if status:
        task.status = status
    
    await db.commit()
    await db.refresh(task)
    return task

# Method 2: Direct update (more efficient for bulk updates)
from sqlalchemy import update

async def mark_tasks_complete(db: AsyncSession, task_ids: list[int]):
    await db.execute(
        update(Task)
        .where(Task.id.in_(task_ids))
        .values(status="completed", is_completed=True)
    )
    await db.commit()
```

**FastAPI route example:**

```python
class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None

@router.patch("/tasks/{task_id}")
async def update_task_endpoint(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update only provided fields
    for field, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    return task
```

### Delete

```python
# Method 1: Fetch and delete
async def delete_task(db: AsyncSession, task_id: int):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        return False
    
    await db.delete(task)
    await db.commit()
    return True

# Method 2: Direct delete
from sqlalchemy import delete

async def delete_completed_tasks(db: AsyncSession):
    await db.execute(
        delete(Task).where(Task.status == "completed")
    )
    await db.commit()
```

**FastAPI route example:**

```python
@router.delete("/tasks/{task_id}")
async def delete_task_endpoint(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await db.delete(task)
    await db.commit()
    return {"message": "Task deleted successfully"}
```

## Querying Data

### Filtering

```python
from sqlalchemy import select, and_, or_, not_

# Simple where clause
result = await db.execute(
    select(Task).where(Task.status == "pending")
)

# Multiple conditions (AND)
result = await db.execute(
    select(Task).where(
        Task.status == "pending",
        Task.is_completed == False
    )
)

# Using and_() explicitly
result = await db.execute(
    select(Task).where(
        and_(
            Task.status == "pending",
            Task.is_completed == False
        )
    )
)

# OR conditions
result = await db.execute(
    select(Task).where(
        or_(
            Task.status == "pending",
            Task.status == "in_progress"
        )
    )
)

# NOT condition
result = await db.execute(
    select(Task).where(not_(Task.is_completed))
)

# IN clause
result = await db.execute(
    select(Task).where(Task.status.in_(["pending", "in_progress"]))
)

# LIKE (pattern matching)
result = await db.execute(
    select(Task).where(Task.title.like("%urgent%"))
)

# Case-insensitive LIKE
result = await db.execute(
    select(Task).where(Task.title.ilike("%urgent%"))
)

# NULL checks
result = await db.execute(
    select(Task).where(Task.description.is_(None))
)
result = await db.execute(
    select(Task).where(Task.description.is_not(None))
)
```

### Ordering

```python
from sqlalchemy import select, desc, asc

# Order by ascending (default)
result = await db.execute(
    select(Task).order_by(Task.created_at)
)

# Order by descending
result = await db.execute(
    select(Task).order_by(desc(Task.created_at))
)

# Multiple order by
result = await db.execute(
    select(Task).order_by(Task.status, desc(Task.created_at))
)
```

### Pagination

```python
# Limit and offset
async def get_tasks_paginated(db: AsyncSession, page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size
    
    result = await db.execute(
        select(Task)
        .order_by(desc(Task.created_at))
        .limit(page_size)
        .offset(offset)
    )
    tasks = result.scalars().all()
    return tasks

# Get total count
from sqlalchemy import func

async def get_total_tasks(db: AsyncSession):
    result = await db.execute(select(func.count(Task.id)))
    total = result.scalar()
    return total
```

### Aggregation

```python
from sqlalchemy import func

# Count
result = await db.execute(select(func.count(Task.id)))
count = result.scalar()

# Count with filter
result = await db.execute(
    select(func.count(Task.id)).where(Task.status == "pending")
)
pending_count = result.scalar()

# Group by
result = await db.execute(
    select(Task.status, func.count(Task.id))
    .group_by(Task.status)
)
status_counts = result.all()  # Returns list of tuples: [("pending", 5), ("completed", 10)]

# Other aggregations
result = await db.execute(select(func.max(Task.created_at)))
latest_date = result.scalar()

result = await db.execute(select(func.min(Task.created_at)))
earliest_date = result.scalar()
```

## Relationships

### One-to-Many

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    
    # Relationship
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="user")

class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="tasks")

# Query with relationships
async def get_user_with_tasks(db: AsyncSession, user_id: int):
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.tasks))  # Eager load tasks
    )
    user = result.scalar_one_or_none()
    return user
```

### Many-to-Many

```python
from sqlalchemy import Table

# Association table
task_tags = Table(
    "task_tags",
    Base.metadata,
    mapped_column("task_id", ForeignKey("tasks.id"), primary_key=True),
    mapped_column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=task_tags,
        back_populates="tasks"
    )

class Tag(Base):
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        secondary=task_tags,
        back_populates="tags"
    )
```

## Advanced Queries

### Joins

```python
from sqlalchemy import select

# Inner join
result = await db.execute(
    select(Task, User)
    .join(User, Task.user_id == User.id)
)

# Left outer join
result = await db.execute(
    select(Task, User)
    .outerjoin(User, Task.user_id == User.id)
)
```

### Subqueries

```python
from sqlalchemy import select

# Subquery
subq = select(Task.user_id).where(Task.status == "completed").subquery()

result = await db.execute(
    select(User).where(User.id.in_(select(subq)))
)
```

### Raw SQL (when needed)

```python
from sqlalchemy import text

# Execute raw SQL
result = await db.execute(
    text("SELECT * FROM tasks WHERE status = :status"),
    {"status": "pending"}
)
tasks = result.fetchall()
```

## Best Practices

### 1. Always Use Dependency Injection

```python
@router.get("/tasks")
async def list_tasks(db: AsyncSession = Depends(get_db)):
    # db session is automatically managed
    pass
```

### 2. Use Pydantic Models for Input/Output

```python
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str | None = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    
    class Config:
        from_attributes = True  # Allows conversion from ORM models
```

### 3. Handle Errors Gracefully

```python
from fastapi import HTTPException

@router.get("/tasks/{task_id}")
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task
```

### 4. Use Transactions for Multiple Operations

```python
async def create_user_with_tasks(db: AsyncSession, user_data: dict, tasks_data: list):
    try:
        # Create user
        user = User(**user_data)
        db.add(user)
        await db.flush()  # Get user.id without committing
        
        # Create tasks
        for task_data in tasks_data:
            task = Task(**task_data, user_id=user.id)
            db.add(task)
        
        # Commit all at once
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        await db.rollback()
        raise e
```

### 5. Use Indexes for Performance

```python
class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String(50), index=True)  # Frequently queried
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
```

### 6. Eager Loading for Relationships

```python
from sqlalchemy.orm import selectinload, joinedload

# Use selectinload for one-to-many (separate query)
result = await db.execute(
    select(User).options(selectinload(User.tasks))
)

# Use joinedload for many-to-one (single query with join)
result = await db.execute(
    select(Task).options(joinedload(Task.user))
)
```

## Quick Reference

### Common Imports

```python
from sqlalchemy import select, insert, update, delete
from sqlalchemy import and_, or_, not_
from sqlalchemy import func, desc, asc
from sqlalchemy import ForeignKey, Table
from sqlalchemy.orm import relationship, selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
```

### Session Operations

```python
db.add(obj)              # Add single object
db.add_all([obj1, obj2]) # Add multiple objects
await db.commit()        # Commit transaction
await db.rollback()      # Rollback transaction
await db.refresh(obj)    # Refresh object from database
await db.flush()         # Flush changes without committing
await db.delete(obj)     # Delete object
```

### Query Results

```python
result.scalar()          # Get single value
result.scalar_one()      # Get single value (error if not exactly one)
result.scalar_one_or_none()  # Get single value or None
result.scalars()         # Get column of values
result.scalars().all()   # Get all values as list
result.all()             # Get all rows as tuples
result.first()           # Get first row
result.fetchall()        # Get all rows (raw SQL)
```

## Additional Resources

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [FastAPI with SQLAlchemy](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [Async SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
