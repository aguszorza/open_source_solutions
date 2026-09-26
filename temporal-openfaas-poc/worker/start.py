import asyncio

from temporalio.client import Client

from workflows.simple_sync_workflow import OpenFaaSSyncWorkflow


async def main():

    client = await Client.connect(
        "localhost:7233",
        namespace="openfaas-poc",
    )

    result = await client.execute_workflow(
        OpenFaaSSyncWorkflow.run,
        args=["Hello from Temporal 2!"],
        id="openfaas-poc-sync-5",
        task_queue="openfaas-poc",
    )

    print("Workflow result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())