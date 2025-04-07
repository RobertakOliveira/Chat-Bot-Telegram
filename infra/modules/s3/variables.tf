variable "owner_tag" {
  description = "Identificador do responsável pelos recursos"
  type        = string
}

variable "common_tags" {
  description = "Tags comuns para todos os recursos"
  type        = map(string)
}