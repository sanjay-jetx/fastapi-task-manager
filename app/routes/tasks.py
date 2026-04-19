from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.dependencies.auth import get_current_user

router = APIRouter()

# Helper to get current user ID
def get_user_by_email(db: Session, email: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# CREATE TASK
@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(
    task: TaskCreate,
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, user_email)
    new_task = Task(title=task.title, owner_id=user.id)

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task

# GET ALL TASKS (only user's tasks) + Pagination + Filtering
@router.get("/tasks", response_model=List[TaskResponse])
def get_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, user_email)

    query = db.query(Task).filter(Task.owner_id == user.id)

    if completed is not None:
        query = query.filter(Task.completed == completed)

    tasks = query.offset(skip).limit(limit).all()

    return tasks

# GET SPECIFIC TASK
@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, user_email)
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

# UPDATE TASK
@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, user_email)
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_update.title is not None:
        task.title = task_update.title
    if task_update.completed is not None:
        task.completed = task_update.completed

    db.commit()
    db.refresh(task)

    return task

# DELETE TASK
@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, user_email)
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return None