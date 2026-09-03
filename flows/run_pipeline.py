from datetime import datetime, timezone

from prefect import flow

from flows.extract_bronze import extract_bronze_flow
from flows.build_silver import build_silver_flow
from flows.build_gold import build_gold_flow


@flow(name="run-full-pipeline")
def run_pipeline_flow():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print("Starting Bronze extraction...")
    extract_bronze_flow()

    print("Starting Silver build...")
    build_silver_flow(bronze_dt=today)

    print("Starting Gold build...")
    build_gold_flow()

    print("Pipeline completed.")


if __name__ == "__main__":
    run_pipeline_flow()