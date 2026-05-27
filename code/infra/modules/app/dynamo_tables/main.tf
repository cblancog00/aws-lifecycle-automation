# Tabla temporal donde los registros tienen un ciclo de vida máximo de 24 horas.
# Los cambios se propagarán a otros components mediante DynamoDB Streams.
resource "aws_dynamodb_table" "temp_db" {
  #checkov:skip=CKV_AWS_119: "Ensure DynamoDB Tables are encrypted using a KMS Customer Managed CMK"
  #checkov:skip=CKV_AWS_28: "Ensure DynamoDB point in time recovery (backup) is enabled"
  name         = local.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  # Clave primaria de tipo string
  attribute {
    name = "id"
    type = "S"
  }

  # TTL: el atributo expiry_time debe set un Unix timestamp (epoch).
  # La aplicación lo calcula como: tiempo_actual + 86400 segundos (24h)
  ttl {
    attribute_name = "expiry_time"
    enabled        = true
  }

  # Streams habilitados para propagar cambios a los consumidores
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
}
