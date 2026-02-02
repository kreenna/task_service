import json
import os

import aio_pika

RABBIT_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")


async def send_task_to_queue(task_id: int):
    """Отправка задания в очередь на выполнение."""

    connection = await aio_pika.connect_robust(RABBIT_URL)
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue("tasks")
        await channel.default_exchange.publish(aio_pika.Message(body=json.dumps({"task_id": task_id}).encode()),
                                               routing_key="tasks")
