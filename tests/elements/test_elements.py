from dataride.configs.elements.environment import Environment
from dataride.configs.elements.module import Module
from dataride.configs.elements.variable import Variable
from dataride.configs.elements.resource import Resource


def test_variable_setup(test_variable_target_name, config_variable, jinja_environment):
    variable = Variable(test_variable_target_name, config_variable, jinja_environment, verbose=False)

    assert variable.name == config_variable["name"]
    assert variable.target == test_variable_target_name
    assert len(variable.template_filled) > 0


def test_resource_setup(resource_name, config_resource, jinja_environment):
    resource = Resource(resource_name, config_resource, jinja_environment, verbose=False)

    assert resource.module == config_resource["_module"]
    assert len(resource.variables) == 1
    assert resource.variables[0].name == "database_name"
    assert resource.variables[0].target == "database_name"


def test_module_empty_setup(module_name, config_module_empty, jinja_environment):
    module = Module(module_name, config_module_empty, jinja_environment, verbose=False)

    assert module.name == module_name
    assert len(module.variables) == 0
    assert len(module.variables_names) == 0
    assert len(module.resources) == 0


def test_environment_setup(config_environment, jinja_environment):
    environment = Environment("test_environment", config_environment, jinja_environment, verbose=False)

    assert environment.name == "test_environment"
    assert len(environment.variables) == 1
    assert environment.variables[0].name == "var_bucket_aws"
    assert environment.variables[0].target == "variable_test"
    assert environment.config["backend"]["type"] == "local"
