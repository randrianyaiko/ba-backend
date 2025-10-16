terraform {
  backend "s3" {
    bucket = "tf-state-store-20251016261"   # create this bucket once manually
    key    = "lambda/terraform.tfstate"      # state file path
    region = "us-east-1"
    encrypt = true
  }
}
