variable "bucket_name_prefix" {
  type        = string
  description = "Prefixo para o nome do bucket S3."
}

variable "bucket_tag_name" {
  type        = string
  description = "Nome para a tag do bucket."
}

variable "project" {
  type        = string
  description = "Nome do projeto."
}

variable "cost_center" {
  type        = string
  description = "Centro de custo associado."
}

variable "dataset_path" {
  type        = string
  description = "Caminho completo até o arquivo ZIP a ser enviado ao bucket."
}

variable "upload_zip" {
  type        = bool
  description = "Indica se o upload do arquivo ZIP deve ser realizado."
  default     = true
}
