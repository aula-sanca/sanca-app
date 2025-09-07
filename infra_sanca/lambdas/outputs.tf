output "asistencia_lambda_arn" {
  description = "ARN de la función Lambda de asistencia"
  value       = aws_lambda_function.asistencia_lambda.arn
}