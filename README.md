
# dataride: lightning-fast data platform setup toolkit

---

## Introduction

**dataride** is a Python package that enables creating data platform infrastructure within seconds for small/medium projects as well as PoCs (Proof of Concept). Its aim is to generate ready-to-deploy code for various frameworks, including Terraform and Apache Airflow. To do the magic, it makes use of YAML configuration files to read data platform features user is willing to set up.  

## Caution

Please bear in mind that no files from `infra_templates/` are ready to be deployed. They contain placeholders within angle brackets (`<` and `>`) to be filled with values, either from user input or default files.
