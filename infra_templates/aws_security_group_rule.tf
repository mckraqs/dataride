resource "aws_security_group_rule" <resource_name> {
  security_group_id = <security_group_id>
{% if source_security_group_id -%}
  source_security_group_id = <source_security_group_id>
{%- endif %}
  type              = <type>
  from_port         = <from_port>
  to_port           = <to_port>
  protocol          = <protocol>

  self              = <is_self_ref>
{%- if prefix_list_ids %}
  prefix_list_ids   = <prefix_list_ids>
{%- endif %}
}