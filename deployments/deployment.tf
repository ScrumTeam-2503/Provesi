# ***************** Universidad de los Andes ***********************
# ********** Arquitectura y diseño de Software - ISIS2503 **********
# ******************** Grupo 6: SCRUM Team *************************
#
# Infraestructura COMPLETA para WMS Provesi con MongoDB + Reportes
# VERSIÓN CORREGIDA - Kong simplificado y funcional
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

variable "mongodb_instance_type" {
  description = "EC2 instance type for MongoDB"
  type        = string
  default     = "t2.small"
}

# ---------- Provider ----------

provider "aws" {
  region = var.region
}

# ---------- Locals ----------

locals {
  project_name = "${var.project_prefix}-wms"
  repository   = "https://github.com/ScrumTeam-2503/Provesi.git"
  branch       = "MongoBranch"

  common_tags = {
    Project   = local.project_name
    ManagedBy = "Terraform"
  }

  ssh_public_keys = [
    "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDUMwSRsL1fYheE3YuIRWyFFzs3/EkbFLCefVW0NOEbsiH1A7LiOSX3AEP339Eqvh+Q9F69mbl/gn5P4kEJkFjpxDExG06DmD16zADqgs+X+nB6wQLLXwmmkX3wICDgBuefbBpL7IxlIyn/hH7AfB0DFVlWV1PZFlQjLLCgBvwhec7r6ut1L8Llb/l+QW6DZBFl6wzmJaFcEptKYkj+8n9MEojvIttH+o2UNabSeSrFqhq7IvkOAbi0pql6MmtUvNAAqDoxfu5K4pht6mNIEwFXovzbskhzUfHKdDiUVhl4uPSzNS8/LCHevZcNxwiOycNC91QuRiRBUN0DEruzz10enyT2K22vJqwcsi+l/LdTYn4mNJ3vFIZjzsnZB7XZFFUfTw9xUHT4nrPwfAh1qF8E24q5toZltNm9rPDC+y9RbgWbGFlixfFMvc1oIrPmMqobveJF1C7QmRyy1bOx3O4Kb+mH0B/86nu3Fx1tsDawaTjsDkMf68B+n7YqZFtA+U3lU4/SEmwrtqRy1beMf/LFcrMcRVVom1XY0iplXPz8jzH/26iJD7pDCCes2BFj6d49/sKOOdNEXLq65Pr86Lfhy2Q4hne4rSfTvgwNhCm+3rePQn94GQ23869scN+IgeueJoF6ySvvRqoO6fWesYq6J1w3dIUjs/SPV/riqDcPcQ==",
    "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDH3xj8egM+NRZ3YQ1WR5hbCQ+OyQhxbVtxXotcDi19E+EVZeeHId1MN+MD/1gLNf/hfyQ0gsxj/NQxjfYzoADTm/gjfOWhM20UQgKW4M4vwaGmFsuxEj2ERSzM8nXRD4YWT8EzpyHb4qwXzNrDtXMTpzi21lPK450TdBKfShjeG/QehbIWT9XBuQT4EzhB4h1mYHHbsabsm/N5XihDyzGzgdynWSnkRNxZLsh5bbo3ScRHnb0CEPIrhcsUwS+fUT0Qdoyu3t8GaDwvQL1cVgY5J7oRgM+c/5P62kui91xHKk9IfkE0Gi0eOWmJPW3YyHCpHic6EqkYIIu25lX5TzXJ+oEm+ksQea7lFF6eD0cfeUcL1R+pAQrdYubZRnCJyqfOPtOvGgF6HRLqQnCbBEh4LsHhvT8pE2pPIW4wti5sWoqOmsy+6CakN9oV3BubnH+SgI5xQaN4uy7ClrtVrrZIka64wTVKgoMpjbrrrvk9vTcjbN6GmLJjSqw/6xFTdL7jHTIkso06Y3SzvPLovXZOyHNI1pdzb6UrK+riz0iNMSRgdKiWjKHyLSVo6VKQbZtpbbff5JHdg8ImzBgFxhDDhWH5tHKbXGU0dSXyDzIj5F13tzJnqIV/zDEf9npUrI/VfcoMZLyY0+lY6gPr1KVVinJ/iO+IG70MCOKcgzlvnw== thefl@Daniel"
  ]
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

# ---------- AMI Amazon Linux 2023 para Kong ----------

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ---------- SSH Key Pair ----------

resource "aws_key_pair" "provesi_team" {
  key_name   = "${var.project_prefix}-team-key"
  public_key = local.ssh_public_keys[0]

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-team-key"
  })
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

resource "aws_security_group" "traffic_reportes" {
  name        = "${var.project_prefix}-traffic-reportes"
  description = "Allow FastAPI Reportes traffic (8000)"

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-traffic-reportes"
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

resource "aws_security_group" "traffic_mongodb" {
  name        = "${var.project_prefix}-traffic-mongodb"
  description = "Allow MongoDB access"

  ingress {
    from_port       = 27017
    to_port         = 27017
    protocol        = "tcp"
    security_groups = [aws_security_group.traffic_django.id]
    description     = "MongoDB from Django instances"
  }

  ingress {
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "MongoDB external access (for debugging)"
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-traffic-mongodb"
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

# ---------- EC2 - PostgreSQL DB ----------

resource "aws_instance" "database" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.provesi_team.key_name
  associate_public_ip_address = true
  vpc_security_group_ids      = [
    aws_security_group.traffic_db.id,
    aws_security_group.traffic_ssh.id
  ]

  user_data = <<-EOT
    #!/bin/bash
    
    echo "${local.ssh_public_keys[1]}" >> /home/ubuntu/.ssh/authorized_keys
    chown ubuntu:ubuntu /home/ubuntu/.ssh/authorized_keys
    chmod 600 /home/ubuntu/.ssh/authorized_keys

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

# ---------- EC2 - MongoDB Instance ----------

resource "aws_instance" "mongodb" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.mongodb_instance_type
  key_name                    = aws_key_pair.provesi_team.key_name
  associate_public_ip_address = true
  vpc_security_group_ids      = [
    aws_security_group.traffic_mongodb.id,
    aws_security_group.traffic_ssh.id
  ]

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  user_data = <<-EOT
    #!/bin/bash
    set -e

    exec > >(tee /var/log/user-data.log)
    exec 2>&1

    echo "${local.ssh_public_keys[1]}" >> /home/ubuntu/.ssh/authorized_keys
    sudo chown ubuntu:ubuntu /home/ubuntu/.ssh/authorized_keys
    sudo chmod 600 /home/ubuntu/.ssh/authorized_keys

    sudo apt-get install -y git
    sudo mkdir -p /proyecto
    cd /proyecto
    sudo git clone -b deployments ${local.repository} Provesi

    # Variables
    DB_NAME="provesi_mongodb"
    DB_USER="provesi_user"
    DB_PASSWORD="scrumteam"

    # Install Docker
    apt-get update -y
    apt-get install -y docker.io
    systemctl start docker
    systemctl enable docker
    usermod -aG docker ubuntu

    # Create MongoDB data directory
    mkdir -p /data/mongodb
    chown -R 999:999 /data/mongodb

    # Create init script for MongoDB
    cat > /tmp/mongo-init.js <<'MONGOEOF'
    db = db.getSiblingDB('provesi_mongodb');
    
    db.createUser({
      user: 'provesi_user',
      pwd: 'scrumteam',
      roles: [
        { role: 'readWrite', db: 'provesi_mongodb' },
        { role: 'dbAdmin', db: 'provesi_mongodb' }
      ]
    });

    db.createCollection('pedidos');
    db.createCollection('productos');
    db.createCollection('bodegas');

    db.pedidos.createIndex({ 'postgres_id': 1 }, { unique: true });
    db.pedidos.createIndex({ 'estado': 1 });
    db.pedidos.createIndex({ 'fecha_creacion': -1 });

    db.productos.createIndex({ 'codigo': 1 }, { unique: true });
    db.productos.createIndex({ 'nombre': 'text', 'descripcion': 'text' });

    db.bodegas.createIndex({ 'codigo': 1 }, { unique: true });
    db.bodegas.createIndex({ 'ciudad': 1 });

    print('MongoDB inicializado correctamente para Provesi WMS');
    MONGOEOF

    mkdir -p /docker-entrypoint-initdb.d
    cp /tmp/mongo-init.js /docker-entrypoint-initdb.d/

    # Run MongoDB with authentication
    docker run -d \
      --name mongodb \
      --restart=always \
      -p 27017:27017 \
      -v /data/mongodb:/data/db \
      -v /docker-entrypoint-initdb.d:/docker-entrypoint-initdb.d:ro \
      -e MONGO_INITDB_ROOT_USERNAME=admin \
      -e MONGO_INITDB_ROOT_PASSWORD=adminpassword \
      -e MONGO_INITDB_DATABASE=provesi_mongodb \
      mongo:7.0 --auth

    # Wait for MongoDB to be ready
    sleep 30

    # Create application user
    docker exec mongodb mongosh --username admin --password adminpassword --authenticationDatabase admin --eval "
    db = db.getSiblingDB('provesi_mongodb');
    try {
      db.createUser({
        user: 'provesi_user',
        pwd: 'scrumteam',
        roles: [
          { role: 'readWrite', db: 'provesi_mongodb' },
          { role: 'dbAdmin', db: 'provesi_mongodb' }
        ]
      });
      print('Usuario creado exitosamente');
    } catch (e) {
      print('Usuario ya existe o error: ' + e);
    }
    "

    echo "MongoDB deployment completed successfully!"
  EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-mongodb",
    Role = "mongodb"
  })
}

# ---------- EC2 - Servicio de Reportes ----------

resource "aws_instance" "servicio_reportes" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.provesi_team.key_name
  associate_public_ip_address = true
  vpc_security_group_ids      = [
    aws_security_group.traffic_reportes.id,
    aws_security_group.traffic_ssh.id
  ]

  user_data = <<-EOT
    #!/bin/bash
    set -e

    exec > >(tee /var/log/user-data.log) 2>&1

    # SSH key
    echo "${local.ssh_public_keys[1]}" >> /home/ec2-user/.ssh/authorized_keys
    chown ec2-user:ec2-user /home/ec2-user/.ssh/authorized_keys
    chmod 600 /home/ec2-user/.ssh/authorized_keys

    # Install Docker
    yum update -y
    yum install -y docker git
    systemctl start docker
    systemctl enable docker
    usermod -aG docker ec2-user

    # Wait for Docker
    sleep 10

    # Clone repository
    mkdir -p /proyecto
    cd /proyecto
    git clone -b ${local.branch} ${local.repository} Provesi || true
    cd Provesi/servicio_reportes

    # Build Docker image
    docker build -t servicio-reportes:latest .

    # Run container
    docker run -d \
      --name servicio-reportes \
      --restart=always \
      -p 8000:8000 \
      -e DATABASE_HOST=${aws_instance.database.private_ip} \
      -e DATABASE_NAME=provesi_db \
      -e DATABASE_USER=provesi_user \
      -e DATABASE_PASSWORD=scrumteam \
      -e DATABASE_PORT=5432 \
      -e MONGODB_HOST=${aws_instance.mongodb.private_ip} \
      -e MONGODB_PORT=27017 \
      -e MONGODB_DATABASE=provesi_mongodb \
      -e MONGODB_USER=provesi_user \
      -e MONGODB_PASSWORD=scrumteam \
      -e MONGODB_AUTH_SOURCE=provesi_mongodb \
      servicio-reportes:latest

    echo "Servicio de Reportes deployment completed!"
  EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-servicio-reportes",
    Role = "servicio-reportes"
  })

  depends_on = [
    aws_instance.database,
    aws_instance.mongodb
  ]
}

# ---------- EC2 - Manejador de Pedidos ----------

resource "aws_instance" "manejador_pedidos" {
  for_each = toset(["a", "b", "c"])

  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.provesi_team.key_name
  associate_public_ip_address = true
  vpc_security_group_ids      = [
    aws_security_group.traffic_django.id,
    aws_security_group.traffic_ssh.id
  ]

  user_data = <<-EOT
    #!/bin/bash
    set -e

    exec > >(tee /var/log/user-data.log) 2>&1

    echo "${local.ssh_public_keys[1]}" >> /home/ubuntu/.ssh/authorized_keys
    chown ubuntu:ubuntu /home/ubuntu/.ssh/authorized_keys
    chmod 600 /home/ubuntu/.ssh/authorized_keys

    apt-get update -y
    apt-get install -y docker.io git
    systemctl start docker
    systemctl enable docker
    usermod -aG docker ubuntu

    sleep 10

    mkdir -p /proyecto
    cd /proyecto
    git clone -b ${local.branch} ${local.repository} Provesi || true
    cd Provesi

    docker build -t manejador-pedidos-app -f manejador_pedidos/Dockerfile .

    docker run -d --name pedidos --restart=always \
      -e DATABASE_HOST=${aws_instance.database.private_ip} \
      -e MONGODB_HOST=${aws_instance.mongodb.private_ip} \
      -e REPORTES_SERVICE_URL=http://${aws_instance.servicio_reportes.private_ip}:8000 \
      -p 8080:8080 \
      manejador-pedidos-app
  EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-manejador-pedidos-${each.key}",
    Role = "manejador-pedidos"
  })

  depends_on = [
    aws_instance.database,
    aws_instance.mongodb,
    aws_instance.servicio_reportes
  ]
}

# ---------- EC2 - Manejador de Inventario ----------

resource "aws_instance" "manejador_inventario" {
  for_each = toset(["a", "b"])

  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.provesi_team.key_name
  associate_public_ip_address = true
  vpc_security_group_ids      = [
    aws_security_group.traffic_django.id,
    aws_security_group.traffic_ssh.id
  ]

  user_data = <<-EOT
    #!/bin/bash
    set -e

    exec > >(tee /var/log/user-data.log) 2>&1

    echo "${local.ssh_public_keys[1]}" >> /home/ubuntu/.ssh/authorized_keys
    chown ubuntu:ubuntu /home/ubuntu/.ssh/authorized_keys
    chmod 600 /home/ubuntu/.ssh/authorized_keys

    apt-get update -y
    apt-get install -y docker.io git
    systemctl start docker
    systemctl enable docker
    usermod -aG docker ubuntu

    sleep 10

    mkdir -p /proyecto
    cd /proyecto
    git clone -b ${local.branch} ${local.repository} Provesi || true
    cd Provesi

    docker build -t manejador-inventario-app -f manejador_inventario/Dockerfile .

    docker run -d --name inventario --restart=always \
      -e DATABASE_HOST=${aws_instance.database.private_ip} \
      -e MONGODB_HOST=${aws_instance.mongodb.private_ip} \
      -e REPORTES_SERVICE_URL=http://${aws_instance.servicio_reportes.private_ip}:8000 \
      -p 8080:8080 \
      manejador-inventario-app
  EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-manejador-inventario-${each.key}",
    Role = "manejador-inventario"
  })

  depends_on = [
    aws_instance.database,
    aws_instance.mongodb,
    aws_instance.servicio_reportes
  ]
}

# ---------- EC2 - Kong API Gateway (CORREGIDO) ----------

resource "aws_instance" "kong" {
  ami                         = "ami-051685736c7b35f95"
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.provesi_team.key_name
  associate_public_ip_address = true

  vpc_security_group_ids = [
    aws_security_group.traffic_app.id,
    aws_security_group.traffic_ssh.id
  ]

  # Si el SO hace shutdown, la instancia pasa a STOP (no se termina de una)
  instance_initiated_shutdown_behavior = "stop"

  # IMPORTANTE: sin base64encode, script directo
  user_data = <<-EOT
#!/bin/bash
exec > /var/log/user-data.log 2>&1
set -x

# --- SSH key para el equipo ---
mkdir -p /home/ec2-user/.ssh
chown ec2-user:ec2-user /home/ec2-user/.ssh
chmod 700 /home/ec2-user/.ssh

echo "${local.ssh_public_keys[1]}" >> /home/ec2-user/.ssh/authorized_keys
chmod 600 /home/ec2-user/.ssh/authorized_keys
chown ec2-user:ec2-user /home/ec2-user/.ssh/authorized_keys

# --- Paquetes básicos ---
dnf install -y docker git || true

# --- Docker ---
systemctl enable docker || true
systemctl start docker || true

# Darle tiempo a Docker
sleep 15

# --- Código del proyecto ---
mkdir -p /proyecto
cd /proyecto || exit 1

if [ ! -d "Provesi" ]; then
  git clone ${local.repository} Provesi || true
fi

cd Provesi || exit 1

# --- Configuración declarativa de Kong ---
cat > /proyecto/Provesi/kong.yml <<'KONGEOF'
_format_version: "2.1"

services:
  - name: manejador_pedidos_service
    host: manejador_pedidos_upstream
    protocol: http
    routes:
      - name: manejador_pedidos
        paths:
          - /
          - /manejador_pedidos
        strip_path: false
        preserve_host: true

  - name: manejador_inventario_service
    host: manejador_inventario_upstream
    protocol: http
    routes:
      - name: manejador_inventario
        paths:
          - /manejador_inventario
        strip_path: false
        preserve_host: true

upstreams:
  - name: manejador_pedidos_upstream
    targets:
      - target: ${aws_instance.manejador_pedidos["a"].private_ip}:8080
      - target: ${aws_instance.manejador_pedidos["b"].private_ip}:8080
      - target: ${aws_instance.manejador_pedidos["c"].private_ip}:8080

  - name: manejador_inventario_upstream
    targets:
      - target: ${aws_instance.manejador_inventario["a"].private_ip}:8080
      - target: ${aws_instance.manejador_inventario["b"].private_ip}:8080
KONGEOF

# --- Red de Docker para Kong ---
docker network create kong-network || true

# Por si ya existe de algún intento anterior
docker rm -f kong 2>/dev/null || true

# --- Contenedor de Kong ---
docker run -d \
  --name kong \
  --network=kong-network \
  --restart=always \
  -v /proyecto/Provesi:/kong/declarative/ \
  -e "KONG_DATABASE=off" \
  -e "KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yml" \
  -p 8000:8000 \
  kong/kong-gateway || true

# Deja viva la instancia un rato por si algo raro
sleep 300
EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-kong",
    Role = "kong-gateway"
  })

  depends_on = [
    aws_instance.manejador_pedidos,
    aws_instance.manejador_inventario
  ]
}

# ---------- EC2 - Manejador de Búsquedas ----------

resource "aws_instance" "manejador_busquedas" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  associate_public_ip_address = true

  vpc_security_group_ids = [
    aws_security_group.traffic_app.id,
    aws_security_group.traffic_ssh.id
  ]

  user_data = <<-EOT
    #!/bin/bash
    set -e
    exec > >(tee /var/log/user-data.log) 2>&1

    echo "PROVESI_DB_HOST=${aws_instance.mongodb.public_ip}" | sudo tee -a /etc/environment

    sudo apt-get update -y
    sudo apt-get install -y python3-pip git python3-venv build-essential

    sudo mkdir -p /proyecto
    cd /proyecto
    sudo git clone https://github.com/ScrumTeam-2503/Manejador_busquedas.git Provesi
    cd Provesi

    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

    sudo tee /etc/systemd/system/provesi-api.service > /dev/null <<EOF
    [Unit]
    Description=Provesi FastAPI
    After=network.target

    [Service]
    User=ubuntu
    WorkingDirectory=/proyecto/Provesi
    ExecStart=/proyecto/Provesi/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
    Restart=always
    Environment=PROVESI_DB_HOST=${aws_instance.mongodb.public_ip}

    [Install]
    WantedBy=multi-user.target
    EOF

    sudo systemctl daemon-reload
    sudo systemctl enable provesi-api
    sudo systemctl start provesi-api
  EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-manejador-busquedas",
    Role = "manejador-busquedas"
  })

  depends_on = [aws_instance.mongodb]
}

# ---------- Outputs ----------

output "kong_public_ip" {
  value       = aws_instance.kong.public_ip
  description = "IP pública de Kong API Gateway"
}

output "database_private_ip" {
  value       = aws_instance.database.private_ip
  description = "IP privada de PostgreSQL"
}

output "database_public_ip" {
  value       = aws_instance.database.public_ip
  description = "IP pública de PostgreSQL"
}

output "mongodb_private_ip" {
  value       = aws_instance.mongodb.private_ip
  description = "IP privada de MongoDB"
}

output "mongodb_public_ip" {
  value       = aws_instance.mongodb.public_ip
  description = "IP pública de MongoDB"
}

output "servicio_reportes_public_ip" {
  value       = aws_instance.servicio_reportes.public_ip
  description = "IP pública del servicio de reportes"
}

output "servicio_reportes_private_ip" {
  value       = aws_instance.servicio_reportes.private_ip
  description = "IP privada del servicio de reportes"
}

output "manejador_pedidos_public_ips" {
  value       = { for id, inst in aws_instance.manejador_pedidos : id => inst.public_ip }
  description = "IPs públicas de pedidos"
}

output "manejador_inventario_public_ips" {
  value       = { for id, inst in aws_instance.manejador_inventario : id => inst.public_ip }
  description = "IPs públicas de inventario"
}

output "quick_access" {
  value = <<-EOT
    
    ╔══════════════════════════════════════════════════════════════════╗
    ║          🚀 PROVESI WMS - INFRAESTRUCTURA DESPLEGADA            ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    🌐 KONG API GATEWAY (Principal):
       URL: http://${aws_instance.kong.public_ip}:8000
       
       Endpoints:
       • Pedidos:     http://${aws_instance.kong.public_ip}:8000/manejador_pedidos/pedidos/
       • Inventario:  http://${aws_instance.kong.public_ip}:8000/manejador_inventario/bodegas/
    
    📊 SERVICIO DE REPORTES:
       Health:     http://${aws_instance.servicio_reportes.public_ip}:8000/health
       API Docs:   http://${aws_instance.servicio_reportes.public_ip}:8000/docs
       Reportes:   http://${aws_instance.servicio_reportes.public_ip}:8000/reportes/inventario
    
    🗄️ BASES DE DATOS:
       PostgreSQL:  ${aws_instance.database.private_ip}:5432
       MongoDB:     ${aws_instance.mongodb.private_ip}:27017
    
    🔧 ACCESO SSH:
       Kong:       ssh -i tu-llave.pem ec2-user@${aws_instance.kong.public_ip}
       Reportes:   ssh -i tu-llave.pem ec2-user@${aws_instance.servicio_reportes.public_ip}
       PostgreSQL: ssh -i tu-llave.pem ubuntu@${aws_instance.database.public_ip}
       MongoDB:    ssh -i tu-llave.pem ubuntu@${aws_instance.mongodb.public_ip}
    
    ⏱️ NOTA: Las instancias tardan ~3-5 minutos en estar completamente operativas
    
    ╚══════════════════════════════════════════════════════════════════╝
  EOT
  description = "URLs y comandos de acceso rápido"
}
