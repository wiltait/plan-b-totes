variable "lambda_name" {
  type    = string
  default = "extract"
}

variable "python_runtime" {
  type    = string
  default = "python3.12"
}

variable "ingested_data_bucket_prefix" {
  type    = string
  default = "will-ingested-data-bucket"
}

variable "processed_data_bucket_prefix" {
  type    = string
  default = "will-processed-data-bucket"
}


variable "code_bucket_prefix" {
  type    = string
  default = "will-code-bucket"
}