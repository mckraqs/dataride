import pytest

from dataride.utils import load_config, prepare_jinja_environment


@pytest.fixture(scope="session")
def jinja_environment():
    return prepare_jinja_environment()


@pytest.fixture(scope="session")
def test_variable_target_name():
    return "tf_variable"


@pytest.fixture(scope="session")
def config_variable():
    return load_config("tests/elements/files/config_variable.yaml")


@pytest.fixture(scope="session")
def resource_name():
    return "aws_glue_crawler"


@pytest.fixture(scope="session")
def module_name():
    return "glue"


@pytest.fixture(scope="session")
def config_resource():
    return load_config("tests/elements/files/config_resource.yaml")


@pytest.fixture(scope="session")
def config_environment():
    return load_config("tests/elements/files/config_environment.yaml")
