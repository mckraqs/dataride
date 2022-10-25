resource "aws_security_group_rule" <resource_name> {
  security_group_id = <sg_id>
  type              = <sgr_type>
  from_port         = <from_port>
  to_port           = <to_port>
  protocol          = <protocol>
  self              = <is_self_ref>
}