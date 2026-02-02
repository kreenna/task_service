import asyncio
import json
import random

import aio_pika
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import update_task_status
from app.database import AsyncSessionLocal
from app.crud import create_task
from app.database import get_db
from app.rabbit import send_task_to_queue
from app.schemas import TaskCreate, TaskResponse

app = FastAPI(title="Task Service")


@app.post("/tasks", response_model=TaskResponse)
async def create_task_endpoint(task_in: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = await create_task(db, task_in)
    await send_task_to_queue(task.id)
    return task.id


async def process_task(task_id: int, db: AsyncSession):
    await update_task_status(db, task_id, "processing")
    await asyncio.sleep(random.uniform(2, 5))  # Имитация
    result = f"Processed: {task_id}"
    await update_task_status(db, task_id, "done", result)


async def main():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("tasks", durable=True)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    data = json.loads(message.body.decode())
                    task_id = data["task_id"]
                    async with AsyncSessionLocal() as db:
                        await process_task(task_id, db)


if __name__ == "__main__":
    asyncio.run(main())
