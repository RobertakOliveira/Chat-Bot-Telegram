provider "aws" {
  alias   = "source"
  region  = var.region
  profile = "<source-profile-name>"
}
