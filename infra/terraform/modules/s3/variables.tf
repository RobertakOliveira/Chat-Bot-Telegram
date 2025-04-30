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

variable "dataset_folder_path" {
  type        = string
  description = "Caminho completo até a pasta 'juridicos' a ser enviada ao bucket."
}