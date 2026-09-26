import httpx

from temporalio import activity


OPENFAAS_GATEWAY = (
    "http://gateway.openfaas.svc.cluster.local:8080"
)

CALLBACK_BASE_URL = (
    "http://temporal-openfaas-callback.temporal.svc.cluster.local:8080"
)


@activity.defn
async def start_openfaas_sync(function_name: str, payload: str) -> str:

    url = (
        f"{OPENFAAS_GATEWAY}"
        f"/function/{function_name}"
    )

    activity.logger.info(
        "Calling OpenFaaS function %s",
        function_name,
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            content=payload,
            timeout=30,
        )

        response.raise_for_status()

        return response.text


@activity.defn
async def start_openfaas_async(
    function_name: str,
    payload: str,
    workflow_id: str,
) -> str:

    url = (
        f"{OPENFAAS_GATEWAY}"
        f"/async-function/{function_name}"
    )

    # The callback service will be deployed in the temporal namespace.
    callback_url = (
        f"{CALLBACK_BASE_URL}"
        f"/callback/{workflow_id}"
    )

    activity.logger.info(
        "Starting async OpenFaaS function: %s",
        function_name,
    )

    async with httpx.AsyncClient() as client:

        response = await client.post(
            url,
            content=payload,
            headers={
                "X-Callback-Url": callback_url,
            },
            timeout=10,
        )

        response.raise_for_status()

        call_id = response.headers.get("X-Call-Id")

        if not call_id:
            raise RuntimeError(
                "OpenFaaS did not return X-Call-Id"
            )

        activity.logger.info(
            "OpenFaaS accepted invocation "
            "function=%s call_id=%s",
            function_name,
            call_id,
        )

        return call_id
