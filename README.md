
# dataride: lightning-fast data platform setup toolkit

---

## Introduction

**dataride** is a Python package that enables creating data platform infrastructure within seconds for small/medium projects as well as PoCs (Proof of Concept). Its aim is to generate ready-to-deploy code for various frameworks, including Terraform and Apache Airflow. To do the magic, it makes use of YAML configuration files to read data platform features that user is willing to set up.

## Requirements

The underlying logic makes a heavy use of Terraform and Jinja templating. Therefore, to fully exploit package features, it's recommended to install Terraform beforehand (possibly one of the latest stable versions). Instructions on how to do this can be found on the [official Terraform tutorial website](https://learn.hashicorp.com/tutorials/terraform/install-cli)

## Examples

Below you can find some examples of running `dataride` CLI, using config examples that were prepared inside `infra_config_examples/` directory

```
dataride create -c infra_config_examples/scenario_aws_s3_and_glue_crawler.yaml -d results/infra_s3_and_glue
```

## Caution

Please bear in mind that no files from `infra_templates/` are ready to be deployed. They contain placeholders within angle brackets (`<` and `>`) to be filled with values, either from user input or default files.
