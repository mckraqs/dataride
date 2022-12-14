import os

from dataride.configs import Infra
from dataride.utils import load_config


def test_scenario_1(jinja_environment, scenario_1_result_tree):
    path = "tests/end2end/files/scenarios/scenario_1"

    scenario_1_config = load_config(f"{path}/config.yaml")
    infra = Infra(scenario_1_config, f"{path}/results", jinja_environment, verbose=False)

    assert len(infra.config["providers"]) == 1
    assert len(infra.config["environments"]) == 1
    assert len(infra.config["resources"]) == 6
    assert len(infra.config["modules"]) == 0
    assert len(infra.config["extra_assets"]) == 1

    infra.process_modules()
    infra.process_resources()
    infra.process_environments()
    infra.process_extra_assets()

    assert len(infra.modules) == 2
    assert len(infra.environments) == 1
    assert len(infra.config["extra_asset_names"]) == 1
    assert infra.config["resource_types"] == [
        "aws_glue_catalog_database",
        "aws_glue_crawler",
        "aws_s3_bucket",
        "aws_s3_directory",
    ]

    infra.save()
    infra.format_code(fmt=True)

    assert len(os.listdir(f"{path}/results")) == 3
    assert len([elem for elem in scenario_1_result_tree if elem not in os.listdir(f"{path}/results")]) == 0


def test_scenario_2(jinja_environment, scenario_2_result_tree):
    path = "tests/end2end/files/scenarios/scenario_2"

    scenario_2_config = load_config(f"{path}/config.yaml")
    infra = Infra(scenario_2_config, f"{path}/results", jinja_environment, verbose=False)

    assert len(infra.config["providers"]) == 1
    assert len(infra.config["environments"]) == 2
    assert len(infra.config["resources"]) == 0
    assert len(infra.config["modules"]) == 1
    assert len(infra.config["extra_assets"]) == 1

    infra.process_modules()
    infra.process_resources()
    infra.process_environments()
    infra.process_extra_assets()

    assert len(infra.modules) == 1
    assert len(infra.environments) == 2
    assert len(infra.resources) == 3
    assert len(infra.config["extra_asset_names"]) == 1
    assert infra.config["resource_types"] == ["aws_s3_bucket", "aws_s3_directory"]

    infra.save()

    assert len(os.listdir(f"{path}/results")) == 4
    assert len([elem for elem in scenario_2_result_tree if elem not in os.listdir(f"{path}/results")]) == 0


def test_scenario_3(jinja_environment, scenario_3_result_tree):
    path = "tests/end2end/files/scenarios/scenario_3"

    scenario_3_config = load_config(f"{path}/config.yaml")
    infra = Infra(scenario_3_config, f"{path}/results", jinja_environment, verbose=False)

    assert len(infra.config["providers"]) == 1
    assert len(infra.config["environments"]) == 3
    assert len(infra.config["resources"]) == 0
    assert len(infra.config["modules"]) == 1
    assert len(infra.config["extra_assets"]) == 1

    infra.process_modules()
    infra.process_resources()
    infra.process_environments()
    infra.process_extra_assets()

    assert len(infra.modules) == 1
    assert len(infra.environments) == 3
    assert len(infra.resources) == 3
    assert len(infra.config["extra_asset_names"]) == 1
    assert infra.config["resource_types"] == ["aws_db_instance", "aws_s3_bucket", "aws_s3_directory"]

    infra.save()

    assert len(os.listdir(f"{path}/results")) == 5
    assert len([elem for elem in scenario_3_result_tree if elem not in os.listdir(f"{path}/results")]) == 0
