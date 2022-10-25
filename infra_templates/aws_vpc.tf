resource "aws_vpc" <resource_name> {
  cidr_block           = <vpc_cidr>
  enable_dns_support   = <enable_dns_support>
  enable_dns_hostnames = <enable_dns_hostnames>
}