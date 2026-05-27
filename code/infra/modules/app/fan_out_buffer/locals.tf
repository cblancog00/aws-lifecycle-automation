locals {
  module_prefix        = "${var.environment}-fan-out-buffer"
  pipe_name            = "${local.module_prefix}-pipe"
  sns_topic_name       = "${local.module_prefix}-topic"
  processor_queue_name = "${local.module_prefix}-processor-queue"
  processor_dlq_name   = "${local.module_prefix}-processor-dlq"
}
