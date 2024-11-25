resource "aws_cloudwatch_event_rule" "scheduler" {
  # this should set up a scheduler that will trigger the Lambda every 20 minutes
  # Careful! other things may need to be set up as well
  name                = "every-twenty-minutes"
  description         = "runs-every-20-minutes"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "lambda-target-20-minutes" {
    rule = aws_cloudwatch_event_rule.scheduler.name
    target_id = "run-extraction"
    arn = aws_lambda_function.extract.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_check_foo" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.extract.function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.scheduler.arn
}