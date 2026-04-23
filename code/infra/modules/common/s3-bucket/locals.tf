locals {
  bucket_name = "${var.env}-${var.bucket_name}-${data.aws_caller_identity.current.account_id}"
}
