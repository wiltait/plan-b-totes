
resource "aws_s3_bucket" "ingested_data_bucket" {
  #Creating s3 bucket to store our ingestion data from extract for project.
  bucket = var.ingested_data_bucket_prefix

  tags = {
    Name        = "My ingested data bucket"
    Environment = "Dev"
  }
}

resource "aws_s3_bucket" "processed_data_bucket" {
  #Creating s3 bucket to store our processed data from extract for project.
  bucket = var.processed_data_bucket_prefix

  tags = {
    Name        = "My processed data bucket"
    Environment = "Dev"
  }
}


resource "aws_s3_bucket" "code_bucket" {
  #Creating s3 bucket to store our code for project.
  bucket = var.code_bucket_prefix

  tags = {
    Name        = "My code bucket"
    Environment = "Dev"
  }
}

resource "aws_s3_object" "extract_lambda_code" {
  bucket = aws_s3_bucket.code_bucket.bucket
  key    = "extract_lambda_function.zip"
  source = "${path.module}/../extract_function.zip"
}

  #Upload the layer code to the code_bucket.
resource "aws_s3_object" "extract_layer_code" {
  bucket = aws_s3_bucket.code_bucket.bucket
  key    = "extract_layer_code.zip"
  source = "${path.module}/../extract_layer.zip"

}
#Upload transform function to code S3
resource "aws_s3_object" "transform_lambda_code" {
  bucket = aws_s3_bucket.code_bucket.bucket
  key    = "transform_lambda_function.zip"
  source = "${path.module}/../transform_function.zip"
}

#Create bucket notification when object is created in s3 
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.ingested_data_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.transform.arn
    events              = ["s3:ObjectCreated:*"]
  }
}
#Allow triggering lambda 
resource "aws_lambda_permission" "s3_trigger" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.transform.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.ingested_data_bucket.arn
}

  
