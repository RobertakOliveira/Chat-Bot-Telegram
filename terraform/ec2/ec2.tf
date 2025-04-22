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

  volume_tags = {
    "Project" = ""
    "CostCenter" = ""
    "Name" = "Chatbot EC2"
  }

  user_data = file("./ec2/start-script.sh")
  security_groups = [aws_security_group.ec2_sg.id]
  subnet_id = aws_subnet.chatbot_public_subnet.id
}

# VPC / SUBNET --------------------------------------------------------------

# VPC
resource "aws_vpc" "chatbot_vpc" {
    cidr_block = "10.0.0.0/24"

    tags = {
        "Name" = "Chatbot VPC"
    }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
    vpc_id = aws_vpc.chatbot_vpc.id

    tags = {
      "Name" = "Chatbot Internet Gateway"
    }
}

# Public Route Table
resource "aws_route_table" "public_route_table" {
    vpc_id = aws_vpc.chatbot_vpc.id

    tags = {
        "Name" = "Chatbot Public Route Table"
    }
}

# Public Route Table Route to Internet Gateway
resource "aws_route" "redirect_to_igw_route" {
    route_table_id = aws_route_table.public_route_table.id # Public Route Table
    gateway_id = aws_internet_gateway.igw.id # Redirect incoming traffic to internet gateway
    destination_cidr_block = "0.0.0.0/0" # All traffic
}

# Chatbot (Public) Subnet
resource "aws_subnet" "chatbot_public_subnet" {
    vpc_id = aws_vpc.chatbot_vpc.id
    cidr_block = "10.0.0.0/25"
    map_public_ip_on_launch = true

    tags = {
      "Name" = "APIGW Public Subnet"
    }
}
resource "aws_route_table_association" "public_subnet_association" { # necessary to bind to correct route table
  route_table_id = aws_route_table.public_route_table.id
  subnet_id = aws_subnet.chatbot_public_subnet.id
}

# EC2 Connect Endpoint -----------------------------------------------------
resource "aws_ec2_instance_connect_endpoint" "chatbot_ec2_connect" {
  subnet_id = aws_subnet.chatbot_public_subnet.id
  security_group_ids = [aws_security_group.ec2_sg.id]
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
    cidr_ipv4 = "0.0.0.0/0" # change this to Telegram's IP
    from_port = 80
    to_port = 80
}

resource "aws_vpc_security_group_ingress_rule" "allow_ssh_ir" {
    security_group_id = aws_security_group.ec2_sg.id
    ip_protocol = "tcp"
    from_port = 22
    to_port = 22
    referenced_security_group_id = aws_security_group.ec2_sg.id # needed to allow EC2 endpoint connection
}

resource "aws_vpc_security_group_egress_rule" "sg_er_1" {
    security_group_id = aws_security_group.ec2_sg.id
    ip_protocol = -1
    cidr_ipv4 = "0.0.0.0/0"
}