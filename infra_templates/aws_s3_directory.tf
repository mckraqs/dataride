resource "aws_s3_bucket_object" <resource_name> {
  bucket       = <bucket>
  key          = <key>
  content_type = "applications/directory"
}