# --------------------------------------------
# Configuración de tablas DynamoDB para app sanca
# --------------------------------------------

# Tabla de escuelas
resource "aws_dynamodb_table" "escuelas" {
  name           = "escuelas"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "cct"

  attribute {
    name = "cct"
    type = "S"
  }
  
  tags = {
    Name        = "escuelas"
    Environment = "dev"
    Project     = "sanca_mvp"
  }
}

# Tabla de grados
resource "aws_dynamodb_table" "grados" {
  name           = "grados"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "escuelaID"
    type = "S"
  }

  global_secondary_index {
    name            = "escuelaID-index"
    hash_key        = "escuelaID"
    projection_type = "ALL"
  }
  
  tags = {
    Name        = "grados"
    Environment = "dev"
    Project     = "sanca_mvp"
  }
}

# Tabla de materias
resource "aws_dynamodb_table" "materias" {
  name           = "materias"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }
  
  tags = {
    Name        = "materias"
    Environment = "dev"
    Project     = "sanca_mvp"
  }
}

# Tabla de maestros
resource "aws_dynamodb_table" "maestros" {
  name           = "maestros"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "escuelaID"
    type = "S"
  }

  global_secondary_index {
    name            = "escuelaID-index"
    hash_key        = "escuelaID"
    projection_type = "ALL"
  }
  
  tags = {
    Name        = "maestros"
    Environment = "dev"
    Project     = "sanca_mvp"
  }
}

# Tabla de tutores
resource "aws_dynamodb_table" "tutores" {
  name           = "tutores"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "escuelaID"
    type = "S"
  }

  global_secondary_index {
    name            = "escuelaID-index"
    hash_key        = "escuelaID"
    projection_type = "ALL"
  }
  
  tags = {
    Name        = "tutores"
    Environment = "dev"
    Project     = "sanca_mvp"
  }
}


# Tabla de alumnos
resource "aws_dynamodb_table" "alumnos" {
  name           = "alumnos"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "escuelaID"
    type = "S"
  }

  attribute {
    name = "gradoID"
    type = "S"
  }

  global_secondary_index {
    name            = "gradoID-index"
    hash_key        = "gradoID"    
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "escuelaID-index"
    hash_key        = "escuelaID"    
    projection_type = "ALL"
  }
  
  tags = {
    Name        = "alumnos"
    Environment = "dev"
    Project     = "sanca_mvp"
  }
}


# Tabla de asistencias
resource "aws_dynamodb_table" "asistencias" {
  name           = "asistencias"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "alumnoID"
  range_key      = "fecha"

  attribute {
    name = "fecha"
    type = "S"
  }
  
  attribute {
    name = "alumnoID"
    type = "S"
  }

  attribute {
    name = "escuelaID"
    type = "S"
  }

  attribute {
    name = "gradoID"
    type = "S"
  }

  global_secondary_index {
    name            = "gradoID-fecha-index"
    hash_key        = "gradoID"
    range_key      = "fecha"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "escuelaID-fecha-index"
    hash_key        = "escuelaID"
    range_key      = "fecha"
    projection_type = "ALL"
  }
  
  tags = {
    Name        = "asistencia"
    Environment = "dev"
    Project     = "sanca_mvp"
  }
}
