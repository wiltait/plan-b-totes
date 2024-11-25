#creates an archive file for extract lambda function. So lambda can use extract.py file.
data "archive_file" "extract_lambda" {
  type             = "zip"
  output_file_mode = "0666"

  source {
    content  = file("${path.module}/../src/extract/__init__.py")
    filename = "__init__.py"
  }

  source {
    content  = file("${path.module}/../src/extract/extract.py")
    filename = "extract.py"
  }

  source {
    content  = file("${path.module}/../src/extract/util_functions.py")
    filename = "util_functions.py"
  }

  output_path      = "${path.module}/../extract_function.zip"
}

resource "aws_lambda_function" "extract" {
  #Creates a Lambda function called extract with dependency layer.
  #Connect the layer which is outlined above
  filename         = "${path.module}/../extract_function.zip"
  function_name    = var.lambda_name
  role             = aws_iam_role.extract_lambda_role.arn
  handler          = "extract.lambda_handler"
  source_code_hash = data.archive_file.extract_lambda.output_base64sha256
  runtime          = var.python_runtime
  layers           = [aws_lambda_layer_version.dependency_layer.arn]
  timeout          = 20
  depends_on       = [aws_lambda_layer_version.dependency_layer]
}

data "archive_file" "transform_lambda" {
  type             = "zip"
  output_file_mode = "0666"

  source {
    content  = file("${path.module}/../src/transform/transform.py")
    filename = "transform.py"
  }
  source {
    content  = file("${path.module}/../src/transform/transform_utils.py")
    filename = "transform_utils.py"
  } 

  output_path = "${path.module}/../transform_function.zip"
}

resource "aws_lambda_function" "transform" {
  filename         = "${path.module}/../transform_function.zip"
  function_name    = "transform"
  role             = aws_iam_role.transform_lambda_role.arn
  handler          = "transform.lambda_handler"
  source_code_hash = data.archive_file.transform_lambda.output_base64sha256
  runtime          = var.python_runtime
  layers           = ["arn:aws:lambda:eu-west-2:336392948345:layer:AWSSDKPandas-Python312:14"]
  timeout          = 120
  depends_on       = [aws_lambda_layer_version.dependency_layer]
}