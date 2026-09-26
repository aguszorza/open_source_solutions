from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities.call_open_faas import (
        start_openfaas_async,
        start_openfaas_sync,
    )


@workflow.defn
class OpenFaaSAsyncWorkflow:

    def __init__(self):
        self.callbacks = {}

    @workflow.signal
    async def openfaas_callback(
        self,
        callback: dict,
    ):

        call_id = callback["call_id"]

        self.callbacks[call_id] = callback

    @workflow.run
    async def run(self, message: str) -> str:

        # 1. Start go-echo asynchronously
        echo_call_id = await workflow.execute_activity(
            start_openfaas_async,
            args=[
                "go-echo",
                message,
                workflow.info().workflow_id,
            ],
            start_to_close_timeout=timedelta(seconds=30),
        )

        workflow.logger.info(
            f"Waiting for go-echo call "
            f"{echo_call_id}"
        )

        # 2. Wait until the callback service signals us
        await workflow.wait_condition(
            lambda: echo_call_id in self.callbacks
        )

        echo_callback = self.callbacks[echo_call_id]

        if echo_callback["status"] != 200:
            raise RuntimeError(
                f"go-echo failed: "
                f"{echo_callback['result']}"
            )

        echo_result = echo_callback["result"]

        workflow.logger.info(
            "go-echo completed"
        )

        # 3. Use the result from go-echo as input to figlet asynchronously
        figlet_call_id = await workflow.execute_activity(
            start_openfaas_async,
            args=[
                "figlet",
                echo_result,
                workflow.info().workflow_id,
            ],
            start_to_close_timeout=timedelta(seconds=30),
        )

        workflow.logger.info(
            f"Waiting for figlet call "
            f"{figlet_call_id}"
        )

        # 4. Wait until the callback service signals us
        await workflow.wait_condition(
            lambda: figlet_call_id in self.callbacks
        )

        figlet_callback = self.callbacks[figlet_call_id]

        if figlet_callback["status"] != 200:
            raise RuntimeError(
                f"figlet failed: "
                f"{figlet_callback['result']}"
            )

        return figlet_callback["result"]
