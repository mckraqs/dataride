resource "aws_redshift_cluster" "<resource_name>" {
  cluster_identifier = <cluster_identifier>

  iam_roles            = [<iam_roles>]
  default_iam_role_arn = <default_iam_role_arn>

  node_type           = <node_type>
  number_of_nodes     = <number_of_nodes>
  port                = <port>
  skip_final_snapshot = <skip_final_snapshot>

  master_username = <master_username>
  master_password = <master_password>
  database_name   = <database_name>

  cluster_subnet_group_name = <cluster_subnet_group_name>
  vpc_security_group_ids    = <vpc_security_group_ids>
}