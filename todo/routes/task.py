from typing import List

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select, update

from todo.auth import AuthenticatedUser
from todo.db import ActiveSession
from todo.models.task import Task, TaskRequest, TaskResponse
from todo.models.user import User

router = APIRouter()


@router.get("/", response_model=List[TaskResponse])
async def list_all_tasks(*, session: Session = ActiveSession):
    """List all tasks"""
    tasks = session.exec(select(Task)).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def task_by_id(*, session: Session = ActiveSession, task_id: int):
    """Get task by task id"""
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@router.get("/me/", response_model=List[TaskResponse])
async def list_all_tasks_by_user(
    *, session: Session = ActiveSession, user: User = AuthenticatedUser
):
    """List all tasks of authenticated user"""
    query = select(Task).where(Task.user_id == user.id)
    tasks = session.exec(query).all()
    return tasks


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    *,
    session: Session = ActiveSession,
    task: TaskRequest,
    user: User = AuthenticatedUser,
):
    '''Create new task'''
    task.user_id = user.id
    
    db_task = Task.from_orm(task)
    
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
