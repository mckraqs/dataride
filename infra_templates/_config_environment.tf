{%- for provider in providers -%}
{%- for provider_name, provider_params in provider.items() -%}
provider "{{ provider_name }}" {
  {%- for param_name, param_value in provider_params.items() %}
  {{ param_name }} = "{{ param_value }}"
  {%- endfor %}
}
{% endfor %}
{% endfor %}


{%- for module_name, module_info in modules.items() %}
module "{{ module_name }}" {
  source = "./../modules/{{ module_name }}"
  {% if module_info['vars_no_def'] %}
  {% for var in module_info['vars_no_def'] -%}
  {% if var not in env['variables_names'] -%}
  {{ var }} = "<ENTER YOUR VARIABLE VALUE HERE>"
  {% else -%}
  {{ var }} = var.{{ var }}
  {% endif %}
  {%- endfor %}
  {%- else %}
  {% endif -%}
}
{% endfor %}

terraform {
  backend "{{ env['backend']['type'] }}" {
    {%- for param_name, param_value in env['backend']['options'].items() %}
    {{ param_name }} = "{{ param_value }}"
    {%- endfor %}
  }
}