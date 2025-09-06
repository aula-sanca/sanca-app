# Región donde se desplegará la infraestructura en AWS
variable "aws_region" {
  default = "mx-central-1"
}

# Dirección IP pública de tu máquina local (con /32 para acceso exclusivo)
# Sustituir por tu ip publica
variable "my_ip" {
  description = "Tu IP pública"
  type        = string
  default     = "XXX.XXX.XXX.XXX/32"
}