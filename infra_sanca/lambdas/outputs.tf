output "asistencia_lambda_arn" {
  description = "ARN de la función Lambda de asistencia"
  value       = aws_lambda_function.asistencia_lambda.arn
}

output "escuela_lambda_arn" {
  description = "ARN de la función Lambda de escuela"
  value       = aws_lambda_function.escuela_lambda.arn
}

output "maestros_lambda_arn" {
  description = "ARN de la función Lambda de maestros"
  value       = aws_lambda_function.maestros_lambda.arn
}

output "alumnos_lambda_arn" {
  description = "ARN de la función Lambda de alumnos"
  value       = aws_lambda_function.alumnos_lambda.arn
}