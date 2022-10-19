{% if 'aws' in platforms %}
provider "aws" {
  region = "eu-central-1" # TODO: move hardcoded parameter to the variable with default value
}
{% else %}
{% endif %}

module "main" {
  source = "./../modules/main"
  # TODO: put variables here somehow
}

# TODO: move everything to be fully manageable by user
# TODO: add description what user should do before applying Terraform (tfstate bucket + dynamodb lock table)
# TODO: add other backend options
terraform {
  backend "s3" {
    key            = "bucket/path/to/terraform.tfstate"
    bucket         = "some-unique-bucket-name"
    region         = "eu-central-1"
    dynamodb_table = "dataride-tf-state-lock-table" # LockID as String for partition key
    encrypt        = true
  }
}