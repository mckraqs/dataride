resource "aws_vpc_endpoint" <resource_name> {
  vpc_id            = <vpc_id>
  service_name      = <service_name> # format("com.amazonaws.%s.s3", var.region)
  vpc_endpoint_type = <endpoint_type>
  route_table_ids   = <route_table_ids>
}