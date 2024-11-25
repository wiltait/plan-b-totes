# Define
resource "aws_lambda_layer_version" "dependency_layer" {
  layer_name          = "dependency_layer"
  compatible_runtimes = [var.python_runtime]
  s3_bucket           = aws_s3_bucket.code_bucket.bucket
  s3_key              = aws_s3_object.extract_layer_code.key
  source_code_hash = filebase64sha256("${path.module}/../extract_layer.zip")
}
