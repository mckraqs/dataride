resource "aws_db_instance" <resource_name> {
  allocated_storage    = <allocated_storage>
  db_name              = <db_name>
  engine               = <engine>
  engine_version       = <engine_version>
  instance_class       = <instance_class>
  username             = <username>
  password             = <password>
  parameter_group_name = <parameter_group_name>
  skip_final_snapshot  = <skip_final_snapshot>
}