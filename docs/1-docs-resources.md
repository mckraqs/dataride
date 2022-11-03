# Resources

## Introduction

Terraform resources are the core functionality of the dataride package. They allow to define infrastructure's objects, divided into environments and modules. 

A properly defined `dataride` resource should have its files inside 2 directories at the repository root level:

* `infra_defaults` - YAML files that contain default values for all resource parameters. If some of them weren't passed, dataride takes the default value and updates the resource dictionary
  * Each of the resources has its parameters, although there are a few (prefixed with an underscore) that are universal across all default configs:
    * `_jinja` - whether a resource should be additionally rendered by the Jinja framework
    * `_module` - to which module resource should be included 
* `infra_templates` - HCL2 files that contain templates for specific resources
  * caution - part of the resource files are additionally templated with [Jinja](https://github.com/pallets/jinja) framework (e.g. `aws_glue_crawler.tf`), so output files structure depends on values passed in the configuration file
    
Moreover, there are a few files that start with the `_config` prefix. They shouldn't be instantiated by the user and are files used by dataride to generate platform setup.

## Resources list

Important information - resources' names match (in the majority of cases) Terraform objects with the corresponding name. Therefore, if you want to research some object more, or if a particular parameter is missing in a template, you can easily refer to Terraform documentation. 

Also, if the below description is not enough, you can check the `infra_defaults` and `infra_templates` directories to see defaults and resource templates.

### aws_eip

Available parameters:

* *is_in_vpc* - optional, default: true

### aws_glue_catalog_database

Available parameters:

* *database_name* - required

### aws_glue_crawler

Available parameters:

* *database_name* - required
* *crawler_role* - required
* *crawler_name* - optional, default: glue_crawler
* *table_prefix* - optional, default: empty string
* *s3_target_path* - optional, default: empty string

### aws_internet_gateway

Available parameters:

* *vpc_id* - optional, default: module variable is created

### aws_nat_gateway

Available parameters:

* *allocation_id* - optional, default: module variable is created
* *subnet_id* - optional, default: module variable is created

### aws_redshift_cluster

Available parameters:

* *cluster_identifier* - optional, default: redshift_cluster
* *iam_roles* - optional, default: module variable is created
* *default_iam_role_arn* - optional, default: module variable is created
* *node_type* - optional, default: dc2.large
* *number_of_nodes* - optional, default: 2
* *port* - optional, default: 5439
* *skip_final_snapshot* - optional, default: true
* *master_username* - optional, default: module variable is created
* *master_password* - optional, default: module variable is created
* *database_name* - optional, default: dev
* *cluster_subnet_group_name* - optional, default: module variable is created
* *vpc_security_group_ids* - optional, default: module variable is created

### aws_redshift_cluster_subnet

Available parameters:

* *cluster_subnet_name* - optional, default: redshift_cluster_subnet
* *subnet_ids* - optional, default: module variable is created

### aws_route_table

Available parameters:

* *basic_route_cidr_block* - required
* *vpc_id* - optional, default: module variable is created
* *gateway_id* - optional, default: empty string
* *nat_gateway_id* - optional, default: empty string


### aws_route_table_association

Available parameters:

* *route_table_id* - optional, default: module variable is created
* *subnet_id* - optional, default: module variable is created

### aws_s3_bucket

Available parameters:

* *bucket_name* - required
* *versioning* - optional, default: module variable is created

### aws_s3_directory

Available parameters:

* *bucket* - required
* *key* - required

### aws_security_group

Available parameters:

* *sg_name* - optional, default: security-group-dataride
* *description* - optional, default: Security group created by dataride.
* *vpc_id* - optional, default: module variable is created

### aws_security_group_rule

Available parameters:

* *security_group_id* - required
* *source_security_group_id* - required
* *type* - required
* *from_port* - required
* *to_port* - required
* *protocol* - required
* *is_self_ref* - optional, default: false
* *prefix_list_ids* - optional

### aws_subnet

Available parameters:

* *vpc_id* - optional, default: module variable is created
* *availability_zone* - optional, default: module variable is created
* *subnet_cidr_block* - optional, default: module variable is created
* *map_public_ip_on_launch* - optional, default: true

### aws_vpc

Available parameters:

* *vpc_cidr* - optional, default: module variable is created
* *enable_dns_support* - optional, default: true
* *enable_dns_hostnames* - optional, default: true

### aws_vpc_endpoint

Available parameters:

* *vpc_id* - optional, default: module variable is created
* *service_name* - optional, default: module variable is created
* *endpoint_type* - optional, default: module variable is created
* *route_table_ids* - optional, default: module variable is created
