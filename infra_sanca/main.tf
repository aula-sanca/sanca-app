# --------------------------------------------
# Proveedor de AWS en la región especificada
# Se usa el profile "terraform" de AWS CLI, creado con aws configure
# --------------------------------------------
provider "aws" {
  region = var.aws_region
  profile = "terraform"
}

module "dynamodb" {
  source = "./dynamodb"
}

module "lambdas" {
  source = "./lambdas"
}

module "apis" {
  source = "./apis"
  asistencia_lambda_arn = module.lambdas.asistencia_lambda_arn
  escuela_lambda_arn = module.lambdas.escuela_lambda_arn
}