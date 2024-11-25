terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.68.0"
    }
  }
    backend "s3" {
    bucket = "will-bucket-tfstate"
    key = "de-s3-file-reader/terraform.tfstate"
    region = "eu-west-2"
  }
}

provider "aws" {
    region = "eu-west-2"
    default_tags {
      tags = {
      ProjectName = "Plan-B-Totes"
      Team = "Cloudy with a chance of Terraform"
      DeployedFrom = "Terraform"
      Repository = "Terrific-Totes"
      CostCentre = "DE"
      Environment = "dev"
    }
  }
}
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}


