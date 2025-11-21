# Implementing the Project Data Model - Step-by-Step Guide

Complete walkthrough for implementing the AI project manager data model in standmate-be.

## 📋 Overview

You'll be creating 11 tables across 7 model files. This guide takes you through each step systematically.

**Estimated time:** 2-3 hours

## 🎯 What You'll Build

- **Projects** - Core project entity
- **Project Inputs** - Speech/transcript data
- **Project Intents** - LLM-extracted scope/constraints
- **Scenarios** - Optimistic/realistic/pessimistic plans
- **Milestones** - High-level project phases
- **Tasks** - Detailed work items with dependencies
- **Risks & Assumptions** - Project uncertainties
- **Conversation Logs** - Speech-to-speech dialogue
- **Project Versions** - Change tracking

---

## Step 1: Create Base Model File

**Why:** Centralize the `Base` class so all models can import it.

### Create `app/models/base.py`

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

**What this does:** Provides a shared base class for all your models.

---

## Step 2: Update Existing Task Model

**Why:** Your existing `task.py` needs to import from the new `base.py` and we'll enhance it later.

### Update `app/models/task.py`

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, Boolean, Date, ForeignKey
from models.base import Base  # Changed from local Base

class Task(Base):
    __tablename__ = "tasks"

    # Existing fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    
    # NEW: Fields for project management
    milestone_id: Mapped[int | None] = mapped_column(ForeignKey("milestones.milestone_id"), nullable=True)
    scenario_id: Mapped[int | None] = mapped_column(ForeignKey("scenarios.scenario_id"), nullable=True)
    duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_start_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    estimated_end_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    critical_path_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Relationships (will be defined after creating other models)
    # milestone: Mapped["Milestone"] = relationship("Milestone", back_populates="tasks")
    # scenario: Mapped["Scenario"] = relationship("Scenario", back_populates="tasks")
```

---

## Step 3: Create User Model (If Needed)

**Why:** Projects need to belong to users.

### Create `app/models/user.py`

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, BigInteger
from datetime import datetime
from models.base import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    
    # Relationships
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="user")
```

**Note:** Adjust fields based on your authentication needs.

---

## Step 4: Create Project Models

**Why:** Core entity that everything else connects to.

### Create `app/models/project.py`

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, BigInteger, Text, Float, ForeignKey
from datetime import datetime
from models.base import Base

class Project(Base):
    __tablename__ = "projects"
    
    project_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    project_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, active, completed, archived
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="projects")
    inputs: Mapped[list["ProjectInput"]] = relationship("ProjectInput", back_populates="project", cascade="all, delete-orphan")
    intents: Mapped[list["ProjectIntent"]] = relationship("ProjectIntent", back_populates="project", cascade="all, delete-orphan")
    scenarios: Mapped[list["Scenario"]] = relationship("Scenario", back_populates="project", cascade="all, delete-orphan")
    risks: Mapped[list["Risk"]] = relationship("Risk", back_populates="project", cascade="all, delete-orphan")
    assumptions: Mapped[list["Assumption"]] = relationship("Assumption", back_populates="project", cascade="all, delete-orphan")
    conversation_logs: Mapped[list["ConversationLog"]] = relationship("ConversationLog", back_populates="project", cascade="all, delete-orphan")
    versions: Mapped[list["ProjectVersion"]] = relationship("ProjectVersion", back_populates="project", cascade="all, delete-orphan")


class ProjectInput(Base):
    __tablename__ = "project_inputs"
    
    input_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.project_id"), nullable=False)
    raw_audio_path: Mapped[str | None] = mapped_column(Text(), nullable=True)
    raw_transcript: Mapped[str | None] = mapped_column(Text(), nullable=True)
    cleaned_transcript: Mapped[str | None] = mapped_column(Text(), nullable=True)
    final_prompt: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="inputs")


class ProjectIntent(Base):
    __tablename__ = "project_intents"
    
    intent_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.project_id"), nullable=False)
    scope: Mapped[str | None] = mapped_column(Text(), nullable=True)
    constraints: Mapped[str | None] = mapped_column(Text(), nullable=True)
    deliverables: Mapped[str | None] = mapped_column(Text(), nullable=True)
    timeline_hints: Mapped[str | None] = mapped_column(Text(), nullable=True)
    extracted_goals: Mapped[str | None] = mapped_column(Text(), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="intents")
```

---

## Step 5: Create Scenario and Milestone Models

**Why:** Scenarios contain milestones which contain tasks.

### Create `app/models/scenario.py`

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, Date, ForeignKey
from datetime import datetime, date
from models.base import Base

class Scenario(Base):
    __tablename__ = "scenarios"
    
    scenario_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.project_id"), nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(20))  # optimistic, realistic, pessimistic
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    estimated_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimated_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="scenarios")
    milestones: Mapped[list["Milestone"]] = relationship("Milestone", back_populates="scenario", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="scenario")


class Milestone(Base):
    __tablename__ = "milestones"
    
    milestone_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scenario_id: Mapped[int] = mapped_column(Integer, ForeignKey("scenarios.scenario_id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    order_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimated_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    
    # Relationships
    scenario: Mapped["Scenario"] = relationship("Scenario", back_populates="milestones")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="milestone")
```

---

## Step 6: Create Task Dependency Model

**Why:** Tasks can depend on other tasks.

### Create `app/models/task_dependency.py`

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey
from models.base import Base

class TaskDependency(Base):
    __tablename__ = "task_dependencies"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.task_id"), nullable=False)
    depends_on_task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.task_id"), nullable=False)
    
    # Relationships
    task: Mapped["Task"] = relationship("Task", foreign_keys=[task_id], back_populates="dependencies")
    depends_on_task: Mapped["Task"] = relationship("Task", foreign_keys=[depends_on_task_id])
```

---

## Step 7: Create Risk and Assumption Models

**Why:** Track project uncertainties.

### Create `app/models/risk.py`

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, ForeignKey
from models.base import Base

class Risk(Base):
    __tablename__ = "risks"
    
    risk_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.project_id"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    likelihood: Mapped[str | None] = mapped_column(String(20), nullable=True)  # low, medium, high
    impact: Mapped[str | None] = mapped_column(String(20), nullable=True)  # low, medium, high
    mitigation_strategy: Mapped[str | None] = mapped_column(Text(), nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="risks")


class Assumption(Base):
    __tablename__ = "assumptions"
    
    assumption_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.project_id"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="assumptions")
```

---

## Step 8: Create Conversation Log Model

**Why:** Track speech-to-speech interactions.

### Create `app/models/conversation.py`

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, ForeignKey
from datetime import datetime
from models.base import Base

class ConversationLog(Base):
    __tablename__ = "conversation_logs"
    
    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.project_id"), nullable=False)
    speaker: Mapped[str | None] = mapped_column(String(20), nullable=True)  # user, huzlr
    audio_path: Mapped[str | None] = mapped_column(Text(), nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text(), nullable=True)
    message_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # question, confirmation, revision, system
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="conversation_logs")
```

---

## Step 9: Create Project Version Model

**Why:** Track changes over time.

### Create `app/models/version.py`

```python
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Text, ForeignKey
from datetime import datetime
from models.base import Base

class ProjectVersion(Base):
    __tablename__ = "project_versions"
    
    version_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.project_id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer)
    change_summary: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="versions")
```

---

## Step 10: Update Task Model with Relationships

**Why:** Complete the bidirectional relationships.

### Update `app/models/task.py` (add relationships)

Add these imports and relationships to your Task model:

```python
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class Task(Base):
    # ... existing fields ...
    
    # Add these relationships
    milestone: Mapped["Milestone"] = relationship("Milestone", back_populates="tasks")
    scenario: Mapped["Scenario"] = relationship("Scenario", back_populates="tasks")
    dependencies: Mapped[list["TaskDependency"]] = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.task_id",
        back_populates="task",
        cascade="all, delete-orphan"
    )
```

---

## Step 11: Generate Migration

**Now that all models are created, generate the migration:**

```bash
cd /Users/gnirmalkumar/Documents/work/standmate-be
source .venv/bin/activate
alembic revision --autogenerate -m "add project management data model"
```

**What to expect:**
```
INFO  [alembic.autogenerate.compare] Detected added table 'users'
INFO  [alembic.autogenerate.compare] Detected added table 'projects'
INFO  [alembic.autogenerate.compare] Detected added table 'project_inputs'
INFO  [alembic.autogenerate.compare] Detected added table 'project_intents'
INFO  [alembic.autogenerate.compare] Detected added table 'scenarios'
INFO  [alembic.autogenerate.compare] Detected added table 'milestones'
INFO  [alembic.autogenerate.compare] Detected added table 'risks'
INFO  [alembic.autogenerate.compare] Detected added table 'assumptions'
INFO  [alembic.autogenerate.compare] Detected added table 'conversation_logs'
INFO  [alembic.autogenerate.compare] Detected added table 'project_versions'
INFO  [alembic.autogenerate.compare] Detected added table 'task_dependencies'
INFO  [alembic.autogenerate.compare] Detected added column 'tasks.milestone_id'
INFO  [alembic.autogenerate.compare] Detected added column 'tasks.scenario_id'
...
```

---

## Step 12: Review the Migration

**Open the generated migration file:**

```bash
# File will be in alembic/versions/xxxx_add_project_management_data_model.py
```

**Check for:**
- ✅ All tables are created
- ✅ Foreign keys are correct
- ✅ Indexes are in place
- ✅ Default values are set

---

## Step 13: Apply Migration

```bash
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade f7f95a9cd9c4 -> abc123def456, add project management data model
```

---

## Step 14: Verify in pgAdmin

1. Open pgAdmin: http://localhost:5050
2. Navigate to: Databases → mydb → Schemas → public → Tables
3. You should see all 11 tables:
   - users
   - projects
   - project_inputs
   - project_intents
   - scenarios
   - milestones
   - tasks (updated)
   - task_dependencies
   - risks
   - assumptions
   - conversation_logs
   - project_versions

---

## Step 15: Test with Sample Data (Optional)

Create a test script to verify relationships work:

```python
# test_models.py
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.project import Project, ProjectInput

async def test_create_project():
    async with AsyncSessionLocal() as session:
        # Create user
        user = User(username="testuser", email="test@example.com")
        session.add(user)
        await session.flush()
        
        # Create project
        project = Project(
            user_id=user.id,
            project_title="Test Project",
            description="Testing the data model"
        )
        session.add(project)
        await session.flush()
        
        # Create project input
        project_input = ProjectInput(
            project_id=project.project_id,
            raw_transcript="Build a mobile app in 3 months"
        )
        session.add(project_input)
        
        await session.commit()
        print(f"✅ Created project {project.project_id} for user {user.username}")

asyncio.run(test_create_project())
```

---

## ✅ Completion Checklist

```
[ ] Created base.py with Base class
[ ] Updated task.py to use base.Base
[ ] Created user.py
[ ] Created project.py (Project, ProjectInput, ProjectIntent)
[ ] Created scenario.py (Scenario, Milestone)
[ ] Created task_dependency.py
[ ] Created risk.py (Risk, Assumption)
[ ] Created conversation.py (ConversationLog)
[ ] Created version.py (ProjectVersion)
[ ] Updated task.py with relationships
[ ] Generated migration
[ ] Reviewed migration file
[ ] Applied migration
[ ] Verified tables in pgAdmin
[ ] Tested with sample data
[ ] Committed changes to git
```

---

## 🎯 Next Steps

After completing this implementation:

1. **Create API routes** for each entity
2. **Add Pydantic schemas** for request/response validation
3. **Implement business logic** for LLM interactions
4. **Add authentication** and user management
5. **Build the speech-to-speech** conversation flow

---

## 📚 Reference

- [SQLAlchemy Guide](SQLALCHEMY_GUIDE.md) - For relationship patterns
- [Migrations Guide](MIGRATIONS_GUIDE.md) - For migration workflows
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/) - Official documentation

Good luck! 🚀
