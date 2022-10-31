import pytest

from dataride.utils import prepare_jinja_environment


@pytest.fixture(scope="session")
def jinja_environment():
    return prepare_jinja_environment()


@pytest.fixture(scope="session")
def config_resource_name():
    return "aws_s3"


@pytest.fixture(scope="session")
def config_s3_bucket_path():
    return "tests/utils/files/test_config_s3_bucket.yaml"


@pytest.fixture(scope="session")
def template_to_load_name():
    return "_config_variable"


@pytest.fixture(scope="session")
def loaded_template_check():
    with open("tests/utils/files/template_check.tf") as f:
        return f.read()


@pytest.fixture(scope="session")
def template_dict():
    return {
        "name": "variable_test",
        "type": "string",
        "description": "This is only a test variable",
        "default_value": "TEST",
    }
