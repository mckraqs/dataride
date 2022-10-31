from .asset_action_required import ActionRequired
from .asset_airflow_local import AirflowLocal

ASSETS_DICT = {"action_required": ActionRequired, "airflow_local": AirflowLocal}
