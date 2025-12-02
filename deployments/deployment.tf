# ***************** Universidad de los Andes ***********************
# ********** Arquitectura y diseño de Software - ISIS2503 **********
# ******************** Grupo 6: SCRUM Team *************************
#
# Infraestructura para WMS de provesi
# ******************************************************************

# ---------- Variables ----------

variable "region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "project_prefix" {
  description = "Prefix used for naming AWS resources"
  type        = string
  default     = "provesi"
}

variable "instance_type" {
  description = "EC2 instance type for application hosts"
  type        = string
  default     = "t2.nano"
}

# ---------- Provider ----------

provider "aws" {
  region = var.region
}

# ---------- Locals ----------

locals {
  project_name = "${var.project_prefix}-wms"
  repository   = "https://github.com/ScrumTeam-2503/Provesi.git"
  branch       = "main"

  common_tags = {
    Project   = local.project_name
    ManagedBy = "Terraform"
  }
}

# ---------- AMI Ubuntu ----------

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ---------- Security Groups ----------

resource "aws_security_group" "traffic_django" {
  name        = "${var.project_prefix}-traffic-django"
  description = "Allow Django traffic (8080)"

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-traffic-services"
  })
}

resource "aws_security_group" "traffic_app" {
  name        = "${var.project_prefix}-traffic-app"
  description = "Expose Kong ports (8000-8001)"

  ingress {
    from_port   = 8000
    to_port     = 8001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-traffic-app"
  })
}

resource "aws_security_group" "traffic_db" {
  name        = "${var.project_prefix}-traffic-db"
  description = "Allow PostgreSQL access"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-traffic-db"
  })
}

resource "aws_security_group" "traffic_ssh" {
  name        = "${var.project_prefix}-traffic-ssh"
  description = "Allow SSH access"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-traffic-ssh"
  })
}

# ---------- EC2 - Kong API Gateway - Load Balancer - Circuit Breaker ----------

resource "aws_instance" "kong" {
  ami                         = "ami-051685736c7b35f95"
  instance_type               = var.instance_type
  associate_public_ip_address = true
  vpc_security_group_ids      = [
    aws_security_group.traffic_app.id,
    aws_security_group.traffic_ssh.id
  ]

  user_data = <<-EOT
    #!/bin/bash

    sudo dnf install nano git -y

    sudo mkdir -p /proyecto
    cd /proyecto
    sudo git clone ${local.repository}
    cd Provesi

    # Insert IPs into kong.yaml
    sed -i "s/<PEDIDOS_A_HOST>/${aws_instance.manejador_pedidos["a"].private_ip}/g" kong.yml
    sed -i "s/<PEDIDOS_B_HOST>/${aws_instance.manejador_pedidos["b"].private_ip}/g" kong.yml
    sed -i "s/<PEDIDOS_C_HOST>/${aws_instance.manejador_pedidos["c"].private_ip}/g" kong.yml

    sed -i "s/<INVENTARIO_A_HOST>/${aws_instance.manejador_inventario["a"].private_ip}/g" kong.yml
    sed -i "s/<INVENTARIO_B_HOST>/${aws_instance.manejador_inventario["b"].private_ip}/g" kong.yml

    docker network create kong-network
    docker run -d --name kong --network=kong-network --restart=always \
      -v "$(pwd):/kong/declarative/" \
      -e "KONG_DATABASE=off" \
      -e "KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yml" \
      -p 8000:8000 kong/kong-gateway
  EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-kong",
    Role = "provesi-kong"
  })

  depends_on = [
    aws_instance.manejador_pedidos,
    aws_instance.manejador_inventario
  ]
}

# ---------- EC2 - PostgreSQL DB ----------

resource "aws_instance" "database" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  associate_public_ip_address = true
  vpc_security_group_ids      = [
    aws_security_group.traffic_db.id,
    aws_security_group.traffic_ssh.id
  ]

  user_data = <<-EOT
    #!/bin/bash
    apt-get update -y
    apt-get install -y docker.io
    docker run --restart=always -d \
      -e POSTGRES_USER=provesi_user \
      -e POSTGRES_DB=provesi_db \
      -e POSTGRES_PASSWORD=scrumteam \
      -p 5432:5432 \
      --name provesi-db postgres
  EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-db",
    Role = "database"
  })
}

# ---------- EC2 - Manejador Pedidos (a, b, c) ----------

resource "aws_instance" "manejador_pedidos" {
  for_each = toset(["a", "b", "c"])

  ami                         = "ami-051685736c7b35f95"
  instance_type               = var.instance_type
  associate_public_ip_address = true
  vpc_security_group_ids      = [
    aws_security_group.traffic_django.id,
    aws_security_group.traffic_ssh.id
  ]

  user_data = <<-EOT
    #!/bin/bash

    export DATABASE_HOST=${aws_instance.database.private_ip}
    echo "DATABASE_HOST=${aws_instance.database.private_ip}" >> /etc/environment

    sudo dnf install nano git docker -y
    sudo systemctl enable docker
    sudo systemctl start docker

    mkdir -p /proyecto
    cd /proyecto

    if [ ! -d Provesi ]; then
      git clone ${local.repository} Provesi
    fi

    cd Provesi

    sudo sed -i "s/<DATABASE_HOST>/${aws_instance.database.private_ip}/g" manejador_pedidos/Dockerfile

    docker build \
      -t manejador-pedidos-app \
      -f manejador_pedidos/Dockerfile \
      .

    docker run -d --name pedidos --restart=always -p 8080:8080 manejador-pedidos-app
  EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-manejador-pedidos-${each.key}",
    Role = "manejador-pedidos"
  })

  depends_on = [aws_instance.database]
}

# ---------- EC2 - Manejador Inventario (a, b) ----------

resource "aws_instance" "manejador_inventario" {
  for_each = toset(["a", "b"])

  ami                         = "ami-051685736c7b35f95"
  instance_type               = var.instance_type
  associate_public_ip_address = true
  vpc_security_group_ids      = [
    aws_security_group.traffic_django.id,
    aws_security_group.traffic_ssh.id
  ]

  user_data = <<-EOT
    #!/bin/bash

    export DATABASE_HOST=${aws_instance.database.private_ip}
    echo "DATABASE_HOST=${aws_instance.database.private_ip}" >> /etc/environment

    sudo dnf install nano git docker -y
    sudo systemctl enable docker
    sudo systemctl start docker

    mkdir -p /proyecto
    cd /proyecto

    if [ ! -d Provesi ]; then
      git clone ${local.repository} Provesi
    fi

    cd Provesi

    sudo sed -i "s/<DATABASE_HOST>/${aws_instance.database.private_ip}/g" manejador_inventario/Dockerfile

    docker build \
      -t manejador-inventario-app \
      -f manejador_inventario/Dockerfile \
      .

    docker run -d --name inventario --restart=always -p 8080:8080 manejador-inventario-app
  EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-manejador-inventario-${each.key}",
    Role = "manejador-inventario"
  })

  depends_on = [aws_instance.database]
}

# ---------- Outputs ----------

output "kong_public_ip" {
  value       = aws_instance.kong.public_ip
}

output "manejador_pedidos_public_ips" {
  value       = { for id, inst in aws_instance.manejador_pedidos : id => inst.public_ip }
}

output "manejador_inventario_public_ip" {
  value       = { for id, inst in aws_instance.manejador_inventario : id => inst.public_ip }
}

output "manejador_pedidos_private_ips" {
  value       = { for id, inst in aws_instance.manejador_pedidos : id => inst.private_ip }
}

output "manejador_inventario_private_ip" {
  value       = { for id, inst in aws_instance.manejador_inventario : id => inst.private_ip }
}

output "database_private_ip" {
  value = aws_instance.database.private_ip
}
