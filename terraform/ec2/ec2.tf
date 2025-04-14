# VARS ---------------------------------------------------------------------

variable "key_name" {
    description = "Key to connect to instance via SSH."
    type = string
}

variable "ssh_ip" {
    description = "IP to allow for SSH connections to the EC2 instance."
    type = string
}

# INSTANCE -----------------------------------------------------------------

resource "aws_instance" "ec2" {
  ami = "ami-00a929b66ed6e0de6" # Amazon Linux 2023 AMI
  instance_type = "t2.micro"
  associate_public_ip_address = true

  tags = {
    "Project" = ""
    "CostCenter" = ""
    "Name" = "Chatbot EC2"
  }

  key_name = var.key_name

  volume_tags = {
    "Project" = ""
    "CostCenter" = ""
    "Name" = "Chatbot EC2"
  }

  user_data_base64 = filebase64("./ec2/start-script.sh")
  security_groups = [aws_security_group.ec2_sg.id]
  subnet_id = aws_subnet.chatbot_subnet.id
}

# VPC / SUBNET --------------------------------------------------------------

# VPC
resource "aws_vpc" "chatbot_vpc" {
    cidr_block = "10.0.0.0/16"
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
    vpc_id = aws_vpc.chatbot_vpc.id
}

# Route
resource "aws_route" "redirect_to_igw_route" {
    route_table_id = aws_vpc.chatbot_vpc.main_route_table_id # VPC's default route table
    gateway_id = aws_internet_gateway.igw.id # Redirect incoming traffic to internet gateway
    destination_cidr_block = "0.0.0.0/0" # All traffic
}

# Public subnet (route table is created automatically on the VPC). EC2 is associated with the subnet.
resource "aws_subnet" "chatbot_subnet" {
    vpc_id = aws_vpc.chatbot_vpc.id
    cidr_block = "10.0.0.0/24"
    map_public_ip_on_launch = true
}

# SECURITY GROUP -----------------------------------------------------------

resource "aws_security_group" "ec2_sg" {
  name = "chatbot_ec2_sg"
  description = "Security group that controls access to chatbot ec2"
  vpc_id = aws_vpc.chatbot_vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "allow_http_ir" {
    security_group_id = aws_security_group.ec2_sg.id
    ip_protocol = "tcp"
    cidr_ipv4 = "0.0.0.0/0"
    from_port = 80
    to_port = 80
}

resource "aws_vpc_security_group_ingress_rule" "allow_ssh_ir" {
    security_group_id = aws_security_group.ec2_sg.id
    ip_protocol = "tcp"
    cidr_ipv4 = var.ssh_ip
    from_port = 22
    to_port = 22
}

resource "aws_vpc_security_group_egress_rule" "sg_er_1" {
    security_group_id = aws_security_group.ec2_sg.id
    ip_protocol = -1
    cidr_ipv4 = "0.0.0.0/0"
}
