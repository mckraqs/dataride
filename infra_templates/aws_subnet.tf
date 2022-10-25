resource "aws_subnet" <resource_name> {
  vpc_id                  = <vpc_id>
  availability_zone       = <availability_zone>
  cidr_block              = <subnet_cidr_block>
  map_public_ip_on_launch = <map_public_ip_on_launch>
}