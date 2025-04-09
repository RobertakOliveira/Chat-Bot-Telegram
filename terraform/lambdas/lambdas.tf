# Based on https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_integration

# Main Lambda ---------------------------------------------

# Lambda needs to be zipped first
data "archive_file" "mainPath" {
    type = "zip"
    source_file = "../functions/Main/Main.py"
    output_path = "./.zip/functions/Main.zip"
}

# Create document for role to be assumed by lambda (give it necessary permissions here)
data "aws_iam_policy_document" "role" {
    statement {
        effect = "Allow"

        principals {
        type        = "Service"
        identifiers = ["lambda.amazonaws.com"]
        }

        actions = ["sts:AssumeRole"]
    }
}

# Create Lambda Permission to be invoked by API Gateway
resource "aws_lambda_permission" "lambda_apigw_invoke_permission" {
  function_name = aws_lambda_function.mainPath.function_name
  principal = "apigateway.amazonaws.com"
  action = "lambda:InvokeFunction"
}

# Create role
resource "aws_iam_role" "lambdarole" {
  name = "lambdarole"
  assume_role_policy = data.aws_iam_policy_document.role.json
}

# Create actual function
variable "bucket_name" {
  type = string  
}

resource "aws_lambda_function" "mainPath" {
    function_name = "MainPath"
    role = aws_iam_role.lambdarole.arn
    filename = "./.zip/functions/Main.zip"
    handler = "Main.lambda_handler"
    runtime = "python3.12"
    source_code_hash = data.archive_file.mainPath.output_sha256 # if changes in source code are made, the hash changes, and Terraform is notices it. See more in https://stackoverflow.com/questions/53477485/terraform-does-not-detect-changes-to-lambda-source-files
    environment {
      variables = {"BUCKET_NAME" = var.bucket_name}
    }
}

# Output --------------------------------------------------

output "mainInvokeARN" {
  value = aws_lambda_function.mainPath.invoke_arn
}