import os
import shutil

import pytest

from dataride.application import Application
from dataride.utils import prepare_jinja_environment


@pytest.fixture(scope="session")
def dataride_application():
    return Application()


@pytest.fixture(scope="session")
def jinja_environment():
    return prepare_jinja_environment()


@pytest.fixture(scope="session")
def scenario_1_result_tree():
    return ["prod", "modules", "action_required.md"]


@pytest.fixture(scope="session", autouse=True)
def end2end_tests_cleanup():
    scenarios_path = "tests/end2end/files/scenarios"
    scenarios = os.listdir(scenarios_path)

    # any scenario doesn't have `results` directory
    assert not any(["results" in os.listdir(f"{scenarios_path}/{scenario_dir}") for scenario_dir in scenarios])

    yield

    # cleaning up scenarios directories
    for scenario_dir in scenarios:
        shutil.rmtree(f"{scenarios_path}/{scenario_dir}/results")

    # any scenario doesn't have `results` directory
    assert not any(["results" in os.listdir(f"{scenarios_path}/{scenario_dir}") for scenario_dir in scenarios])
