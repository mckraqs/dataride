resource "aws_glue_crawler" "<resource_name>" {
  database_name = "<database_name>"
  name          = "<crawler_name>"
  role          = "<crawler_role>"
  table_prefix  = "<table_prefix>"

  {% if s3_target_path != '' %}
  s3_target {
    path = "<s3_target_path>"
  }
  {% else %}
    {{ raise_error("To define AWS Glue Crawler properly, you have to pass at least one target.
    Please verify your config files") }}
  {% endif %}
}