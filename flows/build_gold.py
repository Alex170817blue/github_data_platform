from prefect import flow

from tasks.gold.build_deploy_frequency import build_deploy_frequency
from tasks.gold.build_lead_time_metrics import build_lead_time_metrics
from tasks.gold.build_contributor_activity import build_contributor_activity


@flow(name="build-gold-layer")
def build_gold_flow():
    build_deploy_frequency()
    build_lead_time_metrics()
    build_contributor_activity()

    print("Gold layer build completed.")


if __name__ == "__main__":
    build_gold_flow()