resource "aws_mwaa_environment" <resource_name> {
  name               = <name>
  airflow_version    = <airflow_version>
  execution_role_arn = <execution_role_arn>

  source_bucket_arn    = <source_bucket_arn>
  dag_s3_path          = <dag_s3_path>
  plugins_s3_path      = <plugins_s3_path>
  requirements_s3_path = <requirements_s3_path>

  environment_class = <environment_class>
  min_workers       = <min_workers>
  max_workers       = <max_workers>
  schedulers        = <schedulers>

  webserver_access_mode = <webserver_access_mode>
  network_configuration {
    security_group_ids = <security_group_ids>
    subnet_ids         = <subnet_ids>
  }

  logging_configuration {
    dag_processing_logs {
      enabled   = <dag_processing_logs__enabled>
      log_level = <dag_processing_logs__log_level>
    }

    scheduler_logs {
      enabled   = <scheduler_logs__enabled>
      log_level = <scheduler_logs__log_level>
    }

    task_logs {
      enabled   = <task_logs__enabled>
      log_level = <task_logs__log_level>
    }

    webserver_logs {
      enabled   = <webserver_logs__enabled>
      log_level = <webserver_logs__log_level>
    }

    worker_logs {
      enabled   = <worker_logs__enabled>
      log_level = <worker_logs__log_level>
    }
  }
}