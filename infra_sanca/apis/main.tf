
# Rol IAM para Lambda
resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role_asistencia"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Políticas básicas de ejecución de Lambda
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda Function
resource "aws_lambda_function" "asistencia_lambda" {
  function_name = "asistencia_lambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  filename         = "${path.module}/lambda/handler.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda/handler.zip")
}

# API Gateway REST API (a partir de YAML)
resource "aws_api_gateway_rest_api" "asistencia_api" {
  name = "AsistenciaAPI"

  body = templatefile("${path.module}/api_gateway.yml.tmpl", {
    lambda_arn = aws_lambda_function.asistencia_lambda.arn
  })
}

# Deployment del API
resource "aws_api_gateway_deployment" "asistencia_deploy" {
  rest_api_id = aws_api_gateway_rest_api.asistencia_api.id

  # Forzar nuevo deployment cuando cambie el swagger
  triggers = {
    redeployment = sha1(templatefile("${path.module}/api_gateway.yml.tmpl", {
      lambda_arn = aws_lambda_function.asistencia_lambda.arn
    }))
  }
}

# Stage del API Gateway
resource "aws_api_gateway_stage" "asistencia_stage" {
  rest_api_id   = aws_api_gateway_rest_api.asistencia_api.id
  deployment_id = aws_api_gateway_deployment.asistencia_deploy.id
  stage_name    = "dev"
  description = "Stage de desarrollo para la API de asistencia"
}


# Custom Domain en API Gateway
#resource "aws_api_gateway_domain_name" "asistencia_domain" {
#  domain_name              = "test.api.sanca.com"
#  endpoint_configuration {
#    types = ["REGIONAL"]
#  }
#  regional_certificate_arn          = "arn:aws:acm:mx-central-1:850017501873:certificate/21a07356-92f8-4ead-9ffe-0008b29ab382"
#}

# Asignar el dominio custom al stage de la API
#resource "aws_api_gateway_base_path_mapping" "asistencia_mapping" {
#  api_id = aws_api_gateway_rest_api.asistencia_api.id
#  stage_name  = aws_api_gateway_stage.asistencia_stage.stage_name
#  domain_name = aws_api_gateway_domain_name.asistencia_domain.domain_name
#}

# Permitir que API Gateway invoque el Lambda
resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.asistencia_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.asistencia_api.execution_arn}/*/*"
}
