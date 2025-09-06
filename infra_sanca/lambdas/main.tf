# -------------------------------------------------------------------
# Rol para Lambda
# -------------------------------------------------------------------
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

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


# -------------------------------------------------------------------
# Lambda
# -------------------------------------------------------------------
resource "aws_lambda_function" "asistencia_lambda" {
  function_name = "asistencia_lambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  filename         = "${path.module}/src/lambda_asistencia/lambda_asistencia.zip"
  source_code_hash = filebase64sha256("${path.module}/src/lambda_asistencia/lambda_asistencia.zip")
}