resource "aws_s3_bucket" "<resource_name>" {
  bucket = "<bucket_name>"

  versioning {
    enabled = <versioning>
  }
}