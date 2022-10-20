variable <name> {
  type = <type>

  {%- if default_value is not none %}
  default = <default_value>
  {%- endif -%}
  {%- if description != '' %}
  description = <description>
  {% endif %}
}