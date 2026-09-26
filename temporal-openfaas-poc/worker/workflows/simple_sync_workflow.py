from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities.call_open_faas import start_openfaas_sync


@workflow.defn
class OpenFaaSSyncWorkflow:

    @workflow.run
    async def run(self, message: str) -> str:

        # Step 1: call go-echo
        echo_result = await workflow.execute_activity(
            start_openfaas_sync,
            args=["go-echo", message],
            start_to_close_timeout=timedelta(seconds=30),
        )

        # Step 2: pass the result to figlet
        figlet_result = await workflow.execute_activity(
            start_openfaas_sync,
            args=["figlet", echo_result],
            start_to_close_timeout=timedelta(seconds=30),
        )

        return figlet_result
