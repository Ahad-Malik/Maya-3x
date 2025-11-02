# Minimal Temporal scaffolding for future durability. Not yet wired into app run.
from temporalio.client import Client
from temporalio.worker import Worker


async def run_temporal_worker() -> None:
    client = await Client.connect("localhost:7233")
    # Placeholder: workflows/activities will be registered here once defined
    worker = Worker(client, task_queue="maya_studio", workflows=[], activities=[])
    await worker.run()


