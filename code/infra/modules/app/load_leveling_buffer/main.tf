# EventBridge Pipe: filtra los eventos del stream de DynamoDB y envia solo
# las inserciones nuevas al topic SNS, descartando modificaciones y borrados.
resource "aws_pipes_pipe" "this" {
  name        = local.pipe_name
  role_arn    = aws_iam_role.pipe_role.arn
  source      = var.dynamodb_stream_arn
  target      = aws_sns_topic.this.arn
  description = "Recibe eventos del stream de temp_db y propaga solo inserciones al topic SNS"

  source_parameters {
    dynamodb_stream_parameters {
      starting_position = "LATEST"
      batch_size        = 1
    }

    # Solo se propagan eventos de creacion de registro
    filter_criteria {
      filter {
        pattern = jsonencode({
          eventName = ["INSERT"]
        })
      }
    }
  }

  target_parameters {
    input_template = <<-EOT
    {
      "eventID": "<$.eventID>",
      "eventName": "<$.eventName>",
      "dynamodb": <$.dynamodb>
    }
    EOT
  }
}

# Rol IAM que assume el servicio EventBridge Pipes
resource "aws_iam_role" "pipe_role" {
  name               = "${local.pipe_name}-role"
  assume_role_policy = data.aws_iam_policy_document.assume_pipe_policy.json
}

resource "aws_iam_role_policy" "pipe_policy" {
  name   = "${local.pipe_name}-policy"
  role   = aws_iam_role.pipe_role.id
  policy = data.aws_iam_policy_document.pipe_policy.json
}

# Topic SNS que recibe los eventos filtrados y los distribuye a los suscriptores
resource "aws_sns_topic" "this" {
  #checkov:skip=CKV_AWS_26: "Ensure all data stored in the SNS topic is encrypted"
  name = local.sns_topic_name
}

# Suscripcion SNS → SQS: los mensajes del topic se entregan en la cola principal
resource "aws_sns_topic_subscription" "processor" {
  topic_arn = aws_sns_topic.this.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.processor.arn
}

# Cola principal que recibira los eventos para set procesados por la Lambda
resource "aws_sqs_queue" "processor" {
  #checkov:skip=CKV_AWS_27: "Ensure all data stored in the SQS queue is encrypted"
  name                       = local.processor_queue_name
  visibility_timeout_seconds = 900     # 15 minutos (3x el timeout de Lambda)
  message_retention_seconds  = 1209600 # 14 dias
  receive_wait_time_seconds  = 10      # Long polling

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.processor_dlq.arn
    maxReceiveCount     = 3 # Reintentos antes de enviar a la DLQ
  })
}

# Politica de la cola principal: solo SNS puede enviar mensajes
resource "aws_sqs_queue_policy" "processor" {
  queue_url = aws_sqs_queue.processor.id
  policy    = data.aws_iam_policy_document.processor_queue_policy.json
}

# Cola de mensajes fallidos (DLQ): retiene mensajes que no pudieron procesarse
resource "aws_sqs_queue" "processor_dlq" {
  #checkov:skip=CKV_AWS_27: "Ensure all data stored in the SQS queue is encrypted"
  name                      = local.processor_dlq_name
  message_retention_seconds = 1209600 # 14 dias
}

# Politica de redrive de la DLQ: solo la cola principal puede enviarle mensajes
resource "aws_sqs_queue_redrive_allow_policy" "processor_dlq" {
  queue_url = aws_sqs_queue.processor_dlq.id
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue"
    sourceQueueArns   = [aws_sqs_queue.processor.arn]
  })
}
