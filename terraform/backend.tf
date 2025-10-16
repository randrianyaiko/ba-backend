terraform {
  backend "s3" {
    bucket = "tf-backend-20251016261ba"   # create this bucket once manually
    key    = "lambda/terraform.tfstate"      # state file path
    region = "us-east-1"
    encrypt = true
  }
}
