locals {
  effective_build_script_path = var.build_script_path != null ? var.build_script_path : "${path.module}/build_uv_layer.sh"
  requirements_hash           = filesha1("${var.layer_requirements_path}/${var.layer_requirements_lockfile}")
  script_hash                 = filesha1(local.effective_build_script_path)
  zip_name                    = "${var.layer_name}-${local.requirements_hash}.zip"
}
