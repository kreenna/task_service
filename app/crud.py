from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Task
from .schemas import TaskCreate


async def create_task(db: AsyncSession, task_in: TaskCreate):
    """Создание задания, возвращает его ID."""

    task = Task(payload=task_in.payload)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task.id


async def update_task_status(db: AsyncSession, task_id: int, status: str, result: str = None):
    """Обновление статуса задания с имитацией выполнения (запись результата)."""

    updated = update(Task).where(Task.id == task_id).values(status=status, result=result).execution_options(
        synchronize_session="fetch")
    await db.execute(updated)
    await db.commit()
