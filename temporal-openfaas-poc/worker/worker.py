import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from activities.call_open_faas import start_openfaas_async, start_openfaas_sync
from workflows.simple_sync_workflow import OpenFaaSSyncWorkflow
from workflows.simple_async_workflow import OpenFaaSAsyncWorkflow


async def main():

    client = await Client.connect(
        "temporal-frontend.temporal.svc.cluster.local:7233",
        namespace="openfaas-poc"
    )

    worker = Worker(
        client,
        task_queue="openfaas-poc",
        workflows=[OpenFaaSSyncWorkflow, OpenFaaSAsyncWorkflow],
        activities=[start_openfaas_async, start_openfaas_sync],
    )

    print("Temporal worker started")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
