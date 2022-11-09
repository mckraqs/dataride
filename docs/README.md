# Documentation

1. [Getting started](https://github.com/mckraqs/dataride/tree/main/docs/README.md#Getting-started)
3. [Resources](https://github.com/mckraqs/dataride/tree/main/docs/1-docs-resources.md)
4. [Extra assets](https://github.com/mckraqs/dataride/tree/main/docs/2-docs-assets.md)

---

# Getting started

## Introduction

**dataride** is a Python package that enables creating data platform infrastructure within seconds for small/medium projects as well as PoCs (Proof of Concept). It aims to generate ready-to-deploy code for various frameworks, including tools like Terraform and Apache Airflow. It makes use of YAML configuration files to read data platform features that the user is willing to set up.

## Requirements

The underlying logic makes heavy use of Terraform and Jinja templating. Therefore, to fully exploit package features, it's recommended to install Terraform beforehand (possibly one of the latest stable versions). Instructions on how to do this can be found on the [official Terraform tutorial website](https://learn.hashicorp.com/tutorials/terraform/install-cli).

## Installation

Only one step is required to install the package properly. Use PyPi and run:

```
pip install dataride
```

## How does dataride work?

### YAML infrastructure configuration files

As noted in the introduction, `dataride` makes use of YAML files to set up the infrastructure. It's the only file necessary for processing. The majority of features are taken straight from Terraform. If you don't feel comfortable with the tool, it's highly recommended to revisit its documentation first! 

Below you can find the configuration file's elements that are required to generate infrastructure code: 

* **providers** - list of Terraform providers to specify 
  * to define any provider detailed information, simply put it as an item of a provider's dictionary 
* **environments** - list of environments to create (so far each environment implements all defined Terraform modules) 
    * **variables** - variables list for the environment. Each variable allows to provide:
        * *type* (required)
        * *default_value* (optional)
        * *description* (optional)
* **resources** - list of Terraform resources to provide (see below for more information on resources)
* **extra_assets** - list of additional assets (anything outside Terraform) to provide (see below for more information on extra assets)

An exemplary configuration file can look like this:

```yaml
### Provided structure would generate AWS S3 bucket, directories, and AWS Glue Data Catalog (database and crawler)
### Moreover, local Apache Airflow environment would be prepared 

# List of providers to specify
providers:
  - aws:
      region: eu-central-1

# Terraform environments that instantiate all defined modules
environments:
  prod:
    variables: 
      env:
        type: string
        default_value: prod
  test:
    variables:
      env:
        type: string
        default_value: test

# List of resources to provide
resources:
  - aws_s3_bucket:
      _module: storage
      resource_name: bucket_data
      bucket_name: _format("company-xyz-data-%s", var.env)
      versioning: true
  - aws_s3_directory:
      _module: storage
      bucket: _aws_s3_bucket.bucket_data.name
      key: bronze
  - aws_s3_directory:
      _module: storage
      bucket: _aws_s3_bucket.bucket_data.name
      key: silver
  - aws_s3_directory:
      _module: storage
      bucket: _aws_s3_bucket.bucket_data.name
      key: gold
  - aws_glue_catalog_database:
      _module: glue
      database_name: dc_gold
  - aws_glue_crawler:
      _module: glue
      resource_name: glue_dc_crawler_gold
      database_name: dc_gold
      crawler_role: dataride::arn:iam:123456
      table_prefix: gold_
      s3_target_path: _format("%s/gold", aws_s3_bucket.bucket_data.id)

# Extra assets (apart from the "Action required" document)
extra_assets:
  airflow_local:
```

More configuration examples, including **specific data platform setup scenarios** (highly recommended to check out!), can be found in `config_examples/` at the repository root directory.

### Resources

The main functionality of the `dataride` package is to generate infrastructure setups using Terraform. For the full list of currently available resources, please refer to the [docs-resources](https://github.com/mckraqs/dataride/tree/main/docs/docs-resources.md) document.

**Disclaimer**: if you see some resource missing that you would love to have available, feel free and create a PR! 

### Extra assets

Apart from Terraform resources, there's a functionality to provide additional assets to the infrastructure setup. 

Below you can find a list of available assets:

* **Action required** - even though dataride does the majority of the job, users are still required to perform some final actions, like setting up Terraform backends, or specifying variables that don't have default values. The list of steps is generated automatically, based on an infrastructure setup.
* **Local Apache Airflow environment** - a structure of `dags`, `logs`, and `plugins` directories, as well as Docker Compose file 

For more information, please refer to the [docs-assets](https://github.com/mckraqs/dataride/tree/main/docs/docs-assets.md) document.

### Other information

* **Underscored values** - if any passed value in the configuration file is passed with an underscore (_), it's not treated as a string (which eventually would be quoted in result files), but as an expression (which shouldn't be quoted, but rather passed as is). For example, see bucket_name in the configuration above.
  * Caution - as there's no dynamic hinting, it may be challenging to properly use this feature. If you're not 100% certain, try using a simpler approach first
