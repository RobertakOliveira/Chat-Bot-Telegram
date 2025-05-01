output "vpc_id" {
  value = module.network.vpc_id
}

output "public_subnet_id" {
  value = module.network.public_subnet_id
}

output "docs_bucket_name" {
  value = module.storage.docs_bucket_name
}

output "instance_public_ip" {
  value = module.compute.instance_public_ip
}

output "dashboard_url" {
  value = module.monitoring.dashboard_url
}
