resource "aws_cloudwatch_log_group" "extract_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.extract.function_name}"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_cloudwatch_log_group" "transform_log" {
  name              = "/aws/lambda/transform"
  retention_in_days = 7
}

#Created metric filter for "ERROR" in cw logs.
resource "aws_cloudwatch_log_metric_filter" "extract_error_filter" {
  name           = "MyAppAccessCount"
  pattern        = "\"ERROR\""
  log_group_name = aws_cloudwatch_log_group.extract_log_group.name

  metric_transformation {
    name      = "EventCount"
    namespace = "applicationErrors"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "transform_error_filter" {
  name           = "TransformLambdaErrorFilter"
  log_group_name = aws_cloudwatch_log_group.transform_log.name
  pattern        = "\"ERROR\""

  metric_transformation {
    name      = "TransformLambdaErrorCount"
    namespace = "LambdaErrors"
    value     = "1"
  }
}

#Uses metric_filter to create cloudwatch alarm. Runs once every 2 mins for now.
resource "aws_cloudwatch_metric_alarm" "extract_errors" {
  alarm_name          = "ExtractLambdaErrors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 120
  statistic           = "Sum"
  threshold           = 1
  alarm_actions       = [aws_sns_topic.alert_sre.arn]
  dimensions = {
    "FunctionName" = "extract"
  }
}

resource "aws_cloudwatch_metric_alarm" "transform_errors" {
  alarm_name          = "TransformLambdaErrors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 120
  statistic           = "Sum"
  threshold           = 1
  alarm_actions       = [aws_sns_topic.alert_sre.arn]
  dimensions = {
    "FunctionName" = "transform"
  }
}