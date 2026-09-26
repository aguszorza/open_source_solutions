import asyncio

from temporalio.client import Client

from workflows.simple_async_workflow import OpenFaaSAsyncWorkflow


async def main():

    client = await Client.connect(
        "localhost:7233",
        namespace="openfaas-poc",
    )

    result = await client.execute_workflow(
        OpenFaaSAsyncWorkflow.run,
        args=["Hello from Temporal async!"],
        id="openfaas-async-1",
        task_queue="openfaas-poc",
    )

    print("Workflow result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
