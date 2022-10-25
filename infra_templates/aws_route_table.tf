resource "aws_route_table" <resource_name> {
  vpc_id = <vpc_id>

{% if (<gateway_id>, <nat_gateway_id>)|any %}
  route {
    cidr_block = <basic_route_cidr_block>
{% if <gateway_id> %}
    gateway_id = <gateway_id>
{% elif <nat_gateway_id> %}
    nat_gateway_id = <nat_gateway_id>
{% endif %}
  }
{% endif %}
}