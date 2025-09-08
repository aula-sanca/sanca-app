# API Gateway REST API (a partir de YAML)
resource "aws_api_gateway_rest_api" "sanca_api" {
  name = "SancaAPI"
  body = templatefile("${path.module}/src/api_sanca.yml.tmpl", {
    lambda_asistencia_arn = var.asistencia_lambda_arn,
    lambda_escuela_arn = var.escuela_lambda_arn,
    lambda_maestros_arn = var.maestros_lambda_arn,
    lambda_alumnos_arn = var.alumnos_lambda_arn,
    lambda_tutores_arn = var.tutores_lambda_arn,
    lambda_grados_arn = var.grados_lambda_arn,
    lambda_usuarios_arn = var.usuarios_lambda_arn,
    lambda_materias_arn = var.materias_lambda_arn
  })
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Deployment del API
resource "aws_api_gateway_deployment" "sanca_deploy" {
  rest_api_id = aws_api_gateway_rest_api.sanca_api.id
  
  # Forzar nuevo deployment cuando cambie el swagger
  triggers = {
    redeployment = sha1(templatefile("${path.module}/src/api_sanca.yml.tmpl", {
      lambda_asistencia_arn = var.asistencia_lambda_arn,
      lambda_escuela_arn = var.escuela_lambda_arn,
      lambda_maestros_arn = var.maestros_lambda_arn,
      lambda_alumnos_arn = var.alumnos_lambda_arn,
      lambda_tutores_arn = var.tutores_lambda_arn,
      lambda_grados_arn = var.grados_lambda_arn,
      lambda_usuarios_arn = var.usuarios_lambda_arn,
      lambda_materias_arn = var.materias_lambda_arn
    }))
  }
}

# Stage del API Gateway
resource "aws_api_gateway_stage" "sanca_stage" {
  rest_api_id   = aws_api_gateway_rest_api.sanca_api.id
  deployment_id = aws_api_gateway_deployment.sanca_deploy.id
  stage_name    = "dev"
  description   = "Stage de desarrollo para la API de asistencia"
  lifecycle {
    prevent_destroy = false
  }
}

# Custom Domain en API Gateway
#resource "aws_api_gateway_domain_name" "sanca_domain" {
#  domain_name              = "test.api.sanca.com"
#  endpoint_configuration {
#    types = ["REGIONAL"]
#  }
#  regional_certificate_arn = "arn:aws:acm:mx-central-1:850017501873:certificate/21a07356-92f8-4ead-9ffe-0008b29ab382"
#}

# Asignar el dominio custom al stage de la API
#resource "aws_api_gateway_base_path_mapping" "sanca_mapping" {
#  api_id      = aws_api_gateway_rest_api.sanca_api.id
#  stage_name  = aws_api_gateway_stage.sanca_stage.stage_name
#  domain_name = aws_api_gateway_domain_name.sanca_domain.domain_name
#}

# Permitir que API Gateway invoque el Lambda
resource "aws_lambda_permission" "apigw_invoke_lambda_asistencia" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.asistencia_lambda_arn 
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.sanca_api.execution_arn}/*/*"
}

# Permitir que API Gateway invoque el Lambda
resource "aws_lambda_permission" "apigw_invoke_lambda_escuela" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.escuela_lambda_arn  
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.sanca_api.execution_arn}/*/*"
}

# Permitir que API Gateway invoque el Lambda
resource "aws_lambda_permission" "apigw_invoke_lambda_maestros" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.maestros_lambda_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.sanca_api.execution_arn}/*/*"
}

# Permitir que API Gateway invoque el Lambda
resource "aws_lambda_permission" "apigw_invoke_lambda_alumnos" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.alumnos_lambda_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.sanca_api.execution_arn}/*/*"
}

# Permitir que API Gateway invoque el Lambda
resource "aws_lambda_permission" "apigw_invoke_lambda_tutores" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.tutores_lambda_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.sanca_api.execution_arn}/*/*"
}

# Permitir que API Gateway invoque el Lambda
resource "aws_lambda_permission" "apigw_invoke_lambda_grados" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.grados_lambda_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.sanca_api.execution_arn}/*/*"
}

# Permitir que API Gateway invoque el Lambda
resource "aws_lambda_permission" "apigw_invoke_lambda_usuarios" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.usuarios_lambda_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.sanca_api.execution_arn}/*/*"
}

# Permitir que API Gateway invoque el Lambda
resource "aws_lambda_permission" "apigw_invoke_lambda_materias" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.materias_lambda_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.sanca_api.execution_arn}/*/*"
}