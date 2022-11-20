from .asset_action_required import ActionRequired
from .asset_airflow_local import AirflowLocal
from .asset_mageai_local import MageAILocal

ASSETS_DICT = {"action_required": ActionRequired, "airflow_local": AirflowLocal, "mageai_local": MageAILocal}
