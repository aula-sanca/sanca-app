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
# Política de IAM para acceso a DynamoDB
# -------------------------------------------------------------------
resource "aws_iam_policy" "dynamodb_rw_policy" {
  name        = "dynamodb_rw_policy_asistencia"
  description = "Política para acceso de lectura/escritura a tablas de DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          "arn:aws:dynamodb:*:*:table/asistencias",
          "arn:aws:dynamodb:*:*:table/asistencias/index/*",
          "arn:aws:dynamodb:*:*:table/escuelas",
          "arn:aws:dynamodb:*:*:table/escuelas/index/*",
          "arn:aws:dynamodb:*:*:table/maestros",
          "arn:aws:dynamodb:*:*:table/maestros/index/*",
          "arn:aws:dynamodb:*:*:table/alumnos",
          "arn:aws:dynamodb:*:*:table/alumnos/index/*",
          "arn:aws:dynamodb:*:*:table/tutores",
          "arn:aws:dynamodb:*:*:table/tutores/index/*",
          "arn:aws:dynamodb:*:*:table/grados",
          "arn:aws:dynamodb:*:*:table/grados/index/*",
          "arn:aws:dynamodb:*:*:table/usuarios",
          "arn:aws:dynamodb:*:*:table/usuarios/index/*",
          "arn:aws:dynamodb:*:*:table/materias",
          "arn:aws:dynamodb:*:*:table/materias/index/*"
        ]
      },
      {
        Effect   = "Allow"
        Action   = "dynamodb:DescribeTable"
        Resource = [
          "arn:aws:dynamodb:*:*:table/asistencias",
          "arn:aws:dynamodb:*:*:table/escuelas",
          "arn:aws:dynamodb:*:*:table/maestros",
          "arn:aws:dynamodb:*:*:table/alumnos",
          "arn:aws:dynamodb:*:*:table/tutores",
          "arn:aws:dynamodb:*:*:table/grados",
          "arn:aws:dynamodb:*:*:table/usuarios",
          "arn:aws:dynamodb:*:*:table/materias"
        ]
      }
    ]
  })
}

# -------------------------------------------------------------------
# Adjuntar la política al rol de Lambda
# -------------------------------------------------------------------
resource "aws_iam_role_policy_attachment" "lambda_dynamodb_access" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.dynamodb_rw_policy.arn
}

# -------------------------------------------------------------------
# Lambda asistencia
# -------------------------------------------------------------------
resource "aws_lambda_function" "asistencia_lambda" {
  function_name = "asistencia_lambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  filename      = "${path.module}/src/lambda_asistencia/lambda_asistencia.zip"
  source_code_hash = filebase64sha256("${path.module}/src/lambda_asistencia/lambda_asistencia.zip")
}

# -------------------------------------------------------------------
# Lambda escuela
# -------------------------------------------------------------------
resource "aws_lambda_function" "escuela_lambda" {
  function_name = "escuela_lambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  filename      = "${path.module}/src/lambda_escuela/lambda_escuela.zip"
  source_code_hash = filebase64sha256("${path.module}/src/lambda_escuela/lambda_escuela.zip")
}

# -------------------------------------------------------------------
# Lambda maestros
# -------------------------------------------------------------------
resource "aws_lambda_function" "maestros_lambda" {
  function_name = "maestros_lambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  filename      = "${path.module}/src/lambda_maestros/lambda_maestros.zip"
  source_code_hash = filebase64sha256("${path.module}/src/lambda_maestros/lambda_maestros.zip")
}

# -------------------------------------------------------------------
# Lambda alumnos
# -------------------------------------------------------------------
resource "aws_lambda_function" "alumnos_lambda" {
  function_name = "alumnos_lambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  filename      = "${path.module}/src/lambda_alumnos/lambda_alumnos.zip"
  source_code_hash = filebase64sha256("${path.module}/src/lambda_alumnos/lambda_alumnos.zip")
}

# -------------------------------------------------------------------
# Lambda alumnos
# -------------------------------------------------------------------
resource "aws_lambda_function" "tutores_lambda" {
  function_name = "tutores_lambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  filename      = "${path.module}/src/lambda_tutores/lambda_tutores.zip"
  source_code_hash = filebase64sha256("${path.module}/src/lambda_tutores/lambda_tutores.zip")
}

# -------------------------------------------------------------------
# Lambda grados
# -------------------------------------------------------------------
resource "aws_lambda_function" "grados_lambda" {
  function_name = "grados_lambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  filename      = "${path.module}/src/lambda_grados/lambda_grados.zip"
  source_code_hash = filebase64sha256("${path.module}/src/lambda_grados/lambda_grados.zip")
}

# -------------------------------------------------------------------
# Lambda usuarios
# -------------------------------------------------------------------
resource "aws_lambda_function" "usuarios_lambda" {
  function_name = "usuarios_lambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  filename      = "${path.module}/src/lambda_usuarios/lambda_usuarios.zip"
  source_code_hash = filebase64sha256("${path.module}/src/lambda_usuarios/lambda_usuarios.zip")
}

# -------------------------------------------------------------------
# Lambda materias
# -------------------------------------------------------------------
resource "aws_lambda_function" "materias_lambda" {
  function_name = "materias_lambda"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  filename      = "${path.module}/src/lambda_materias/lambda_materias.zip"
  source_code_hash = filebase64sha256("${path.module}/src/lambda_materias/lambda_materias.zip")
}