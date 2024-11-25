#Creates an SNS alert topic.
resource "aws_sns_topic" "alert_sre" {
  name = "alert-sre"
}

#Creates an SNS subscription to allow emails to be sent to given email address
resource "aws_sns_topic_subscription" "sre_email_subscription" {
  topic_arn = aws_sns_topic.alert_sre.arn
  protocol  = "email"
  endpoint  = "wiltait@gmail.com"
}
