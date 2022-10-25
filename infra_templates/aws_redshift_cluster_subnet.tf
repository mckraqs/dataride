resource "aws_redshift_subnet_group" <resource_name> {
  name       = <cluster_subnet_name>
  subnet_ids = <subnet_ids>
}