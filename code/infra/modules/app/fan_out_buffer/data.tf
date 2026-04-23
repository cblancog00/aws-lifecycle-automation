data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Politica de confianza para que el servicio EventBridge Pipes asuma el rol
data "aws_iam_policy_document" "assume_pipe_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["pipes.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

# Permisos del rol de la pipe: leer del stream y publicar en SNS
data "aws_iam_policy_document" "pipe_policy" {
  statement {
    sid = "LeerStreamDynamoDB"
    actions = [
      "dynamodb:DescribeStream",
      "dynamodb:GetRecords",
      "dynamodb:GetShardIterator",
      "dynamodb:ListStreams"
    ]
    resources = [var.dynamodb_stream_arn]
  }

  statement {
    sid       = "PublicarEnSNS"
    actions   = ["sns:Publish"]
    resources = [aws_sns_topic.this.arn]
  }
}

# Politica de la cola SQS principal: solo el topic SNS puede enviar mensajes
data "aws_iam_policy_document" "processor_queue_policy" {
  statement {
    sid    = "PermitirEnvioDesdesSNS"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }

    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.processor.arn]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_sns_topic.this.arn]
    }
  }
}
