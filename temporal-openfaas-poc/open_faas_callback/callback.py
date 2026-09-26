from fastapi import FastAPI, Request
from temporalio.client import Client

import uvicorn


app = FastAPI()

temporal_client = None


@app.on_event("startup")
async def startup():

    global temporal_client

    temporal_client = await Client.connect(
        "temporal-frontend.temporal.svc.cluster.local:7233",
        namespace="openfaas-poc",
    )


@app.post("/callback/{workflow_id}")
async def callback(workflow_id: str, request: Request):

    body = await request.body()
    result = body.decode("utf-8")

    function_name = request.headers.get(
        "X-Function-Name",
        "unknown",
    )

    call_id = request.headers.get(
        "X-Call-Id",
        "unknown",
    )

    function_status = request.headers.get(
        "X-Function-Status",
        "500",
    )

    retry = request.headers.get(
        "X-Retry"
    )

    retry_max = request.headers.get(
        "X-Retry-Max"
    )

    print(
        "OpenFaaS callback:"
        f" workflow={workflow_id}"
        f" function={function_name}"
        f" call_id={call_id}"
        f" status={function_status}"
        f" retry={retry}/{retry_max}"
    )

    if not call_id:
        return {
            "status": "error",
            "message": "Missing X-Call-Id",
        }

    handle = temporal_client.get_workflow_handle(
        workflow_id
    )

    await handle.signal(
        "openfaas_callback",
        {
            "call_id": call_id,
            "function_name": function_name,
            "status": int(function_status),
            "result": result,
        },
    )

    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
    )
