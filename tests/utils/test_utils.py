from jinja2 import Environment

from dataride.utils import (
    load_config,
    load_template,
    update_resource_dict_with_defaults,
    render_jinja,
    fill_template_values,
)


def test_jinja_environment(jinja_environment):
    assert isinstance(jinja_environment, Environment)
    assert (
        "raise_error" in jinja_environment.globals.keys()
        and "intersection" in jinja_environment.globals.keys()
        and "any" in jinja_environment.filters.keys()
    )
    assert callable(jinja_environment.globals["raise_error"])
    assert callable(jinja_environment.globals["intersection"])
    assert callable(jinja_environment.filters["any"])


def test_load_config(config_s3_bucket_path):
    config_loaded = load_config(config_s3_bucket_path)
    assert list(config_loaded.keys()) == ["_jinja", "resource_name"]


def test_load_template(template_to_load_name, loaded_template_check):
    loaded_template = load_template(template_to_load_name)
    assert loaded_template == loaded_template_check


def test_update_resource_dict_with_defaults(config_s3_bucket_path, config_resource_name):
    resource_dict = load_config(config_s3_bucket_path)
    assert "_jinja" in list(resource_dict.keys())
    assert "_module" not in list(resource_dict.keys())
    assert "versioning" not in list(resource_dict.keys())

    resource_dict_updated = update_resource_dict_with_defaults(resource_dict, config_resource_name)
    assert "_jinja" in list(resource_dict_updated.keys())
    assert "_module" in list(resource_dict_updated.keys())
    assert "versioning" in list(resource_dict_updated.keys())


def test_render_jinja(template_to_load_name, template_dict, jinja_environment):
    template = load_template(template_to_load_name)
    template_rendered = render_jinja(template, template_dict, jinja_environment)
    assert template_dict["name"] not in template_rendered
    assert template_dict["description"] not in template_rendered
    assert "{%" not in template_rendered and "%}" not in template_rendered
    assert "<description>" in template_rendered


def test_fill_template_values(template_to_load_name, template_dict, jinja_environment):
    template = load_template(template_to_load_name)
    template_rendered = render_jinja(template, template_dict, jinja_environment)
    template_filled = fill_template_values(template_rendered, template_dict)
    assert template_dict["name"] in template_filled
    assert template_dict["description"] in template_filled
    assert "{%" not in template_filled and "%}" not in template_filled
