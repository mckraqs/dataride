
# dataride: lightning-fast data platform setup toolkit

---

## Introduction

**dataride** is a Python package that enables creating data platform infrastructure within seconds for small/medium projects as well as PoCs (Proof of Concept). It aims to generate ready-to-deploy code for various frameworks, including tools like Terraform and Apache Airflow. It makes use of YAML configuration files to read data platform features that the user is willing to set up.

## Requirements

The underlying logic makes heavy use of Terraform and Jinja templating. Therefore, to fully exploit package features, it's recommended to install Terraform beforehand (possibly one of the latest stable versions). Instructions on how to do this can be found on the [official Terraform tutorial website](https://learn.hashicorp.com/tutorials/terraform/install-cli).

## Example

Below you can find and example of running the `dataride` CLI, using config examples that were prepared inside the `config_examples/` directory. It takes **20 seconds** to go from ready config file to infrastructure setup generation. 

```
dataride create -c config_examples/scenario_aws_s3_and_data_catalog.yaml -d results/infra_s3_and_glue
```

![dataride_showcase](https://raw.githubusercontent.com/mckraqs/dataride/main/media/example_showcase.gif)

## Documentation

For further description of the package's features, please refer to [docs](https://github.com/mckraqs/dataride/tree/main/docs) directory. All the necessary information is stored there.

## Collaboration

If you see any room for improvement, feel free to submit a PR! Let's develop dataride to suit as many data teams as possible.
