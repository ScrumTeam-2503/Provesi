# ***************** Universidad de los Andes ***********************
# ********** Arquitectura y diseño de Software - ISIS2503 **********
# ******************** Grupo 6: SCRUM Team *************************
#
# Infraestructura para WMS de provesi con MongoDB + Servicio Reportes
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
  default     = "t2.small"  # MongoDB necesita más RAM
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

  # Llaves SSH públicas
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

# ---------- SSH Key Pair ----------

resource "aws_key_pair" "provesi_team" {
  key_name   = "${var.project_prefix}-team-key"
  public_key = local.ssh_public_keys[0]  # Primera llave como principal

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
  description = "Allow MongoDB access from Django instances"

  # MongoDB desde instancias Django
  ingress {
    from_port       = 27017
    to_port         = 27017
    protocol        = "tcp"
    security_groups = [aws_security_group.traffic_django.id]
    description     = "MongoDB from Django instances"
  }

  # MongoDB para debugging (opcional, comentar en producción)
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

  # Aumentar el tamaño del disco para MongoDB
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  user_data = <<-EOT
    #!/bin/bash
    set -e

    # Logging
    exec > >(tee /var/log/user-data.log)
    exec 2>&1

    echo "======================================"
    echo "🔑 Configurando llaves SSH adicionales"
    echo "======================================"

    # Agregar segunda llave SSH al usuario ubuntu
    echo "${local.ssh_public_keys[1]}" >> /home/ubuntu/.ssh/authorized_keys
    sudo chown ubuntu:ubuntu /home/ubuntu/.ssh/authorized_keys
    sudo chmod 600 /home/ubuntu/.ssh/authorized_keys

    echo "======================================"
    echo "📁 Clonando repositorio"
    echo "======================================"

    # Instalar git
    sudo apt-get install -y git

    # Clonar repositorio en la rama deployments
    sudo mkdir -p /proyecto
    cd /proyecto
    sudo git clone -b deployments ${local.repository} Provesi

    echo "======================================"
    echo "🚀 Instalando MongoDB 7.0"
    echo "======================================"

    # Actualizar sistema
    sudo apt-get update -y
    sudo apt-get upgrade -y

    # Instalar dependencias
    sudo apt-get install -y curl gnupg

    # 1. Importar clave GPG
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
      sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/mongodb-server-7.0.gpg

    # 2. Agregar repositorio
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
      sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

    # 3. Actualizar
    sudo apt-get update

    # 4. Instalar MongoDB
    sudo apt-get install -y mongodb-org

    # 5. Crear directorios
    sudo mkdir -p /var/lib/mongodb
    sudo mkdir -p /var/log/mongodb
    sudo chown -R mongodb:mongodb /var/lib/mongodb
    sudo chown -R mongodb:mongodb /var/log/mongodb

    # 6. Configurar
    sudo tee /etc/mongod.conf > /dev/null <<'EOF'
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
  wiredTiger:
    engineConfig:
      cacheSizeGB: 0.5

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
  logRotate: reopen

net:
  port: 27017
  bindIp: 0.0.0.0

security:
  authorization: enabled

processManagement:
  timeZoneInfo: /usr/share/zoneinfo
  fork: false

operationProfiling:
  mode: slowOp
  slowOpThresholdMs: 100
EOF

    # 7. Iniciar
    sudo systemctl daemon-reload
    sudo systemctl start mongod
    sudo systemctl enable mongod

    # 8. Verificar
    sleep 5
    sudo systemctl status mongod

    echo ""
    echo "======================================"
    echo "✅ MongoDB instalado"
    echo "======================================"

    # Esperar que MongoDB esté listo
    sleep 10

    echo "======================================"
    echo "👤 Configurando usuarios"
    echo "======================================"

    # Crear usuario admin (primera vez sin auth)
    mongosh admin --eval '
    db.createUser({
      user: "admin",
      pwd: "scrumteam_admin_2024",
      roles: [{ role: "root", db: "admin" }]
    })
    ' || echo "Usuario admin ya existe"

    # Crear base de datos y usuario de aplicación
    mongosh -u admin -p scrumteam_admin_2024 --authenticationDatabase admin <<'EOMONGO'
    use provesi_mongodb

    db.createUser({
      user: "provesi_user",
      pwd: "scrumteam",
      roles: [
        { role: "readWrite", db: "provesi_mongodb" },
        { role: "dbAdmin", db: "provesi_mongodb" }
      ]
    })

    db.createCollection("pedidos")
    db.createCollection("productos")
    db.createCollection("bodegas")

    db.pedidos.createIndex({ "postgres_id": 1 }, { unique: true })
    db.pedidos.createIndex({ "estado": 1, "fecha_creacion": -1 })
    db.productos.createIndex({ "codigo": 1 }, { unique: true })
    db.productos.createIndex({ "nombre": "text" })
    db.bodegas.createIndex({ "codigo": 1 }, { unique: true })

    print("✅ Base de datos y usuarios configurados")
    EOMONGO

    echo ""
    echo "======================================"
    echo "✅ MongoDB listo!"
    echo "======================================"
    echo "Host: $(hostname -I | awk '{print $1}')"
    echo "Puerto: 27017"
    echo "Base de datos: provesi_mongodb"
    echo "Usuario: provesi_user"
    echo "Password: scrumteam"

    # Verificar conexión
    mongosh -u provesi_user -p scrumteam --authenticationDatabase provesi_mongodb provesi_mongodb --eval "db.getCollectionNames()"

  EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-mongodb",
    Role = "mongodb"
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
    
    # Agregar segunda llave SSH al usuario ubuntu
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

# ---------- EC2 - Servicio de Reportes ----------

resource "aws_instance" "servicio_reportes" {
  ami                         = "ami-051685736c7b35f95"  # Amazon Linux 2
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

    # Logging
    exec > >(tee /var/log/user-data.log)
    exec 2>&1

    echo "======================================"
    echo "🔑 Configurando llaves SSH"
    echo "======================================"

    # Agregar segunda llave SSH
    echo "${local.ssh_public_keys[1]}" >> /home/ec2-user/.ssh/authorized_keys
    chown ec2-user:ec2-user /home/ec2-user/.ssh/authorized_keys
    chmod 600 /home/ec2-user/.ssh/authorized_keys

    echo "======================================"
    echo "📦 Instalando dependencias"
    echo "======================================"

    # Instalar Docker y Git
    sudo dnf install nano git docker -y
    sudo systemctl enable docker
    sudo systemctl start docker

    echo "======================================"
    echo "📁 Clonando repositorio"
    echo "======================================"

    # Clonar repositorio
    mkdir -p /proyecto
    cd /proyecto

    if [ ! -d Provesi ]; then
      git clone ${local.repository} Provesi
    fi

    cd Provesi/servicio_reportes

    echo "======================================"
    echo "🐳 Construyendo imagen Docker"
    echo "======================================"

    # Build imagen Docker
    docker build -t servicio-reportes:latest .

    echo "======================================"
    echo "🚀 Ejecutando servicio de reportes"
    echo "======================================"

    # Ejecutar contenedor con IPs reales inyectadas
    docker run -d --name servicio-reportes --restart=always \
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

    echo ""
    echo "======================================"
    echo "✅ Servicio de reportes desplegado"
    echo "======================================"
    echo "URL: http://$(hostname -I | awk '{print $1}'):8000"
    echo "Health Check: http://$(hostname -I | awk '{print $1}'):8000/health"
    echo "Documentación: http://$(hostname -I | awk '{print $1}'):8000/docs"
    echo ""
    echo "Conexiones configuradas:"
    echo "  PostgreSQL: ${aws_instance.database.private_ip}:5432"
    echo "  MongoDB: ${aws_instance.mongodb.private_ip}:27017"

    # Verificar que el contenedor esté corriendo
    sleep 5
    docker ps | grep servicio-reportes || echo "⚠️ Contenedor no está corriendo"

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

# ---------- EC2 - Manejador Pedidos (a, b, c) ----------

resource "aws_instance" "manejador_pedidos" {
  for_each = toset(["a", "b", "c"])

  ami                         = "ami-051685736c7b35f95"
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.provesi_team.key_name
  associate_public_ip_address = true
  vpc_security_group_ids      = [
    aws_security_group.traffic_django.id,
    aws_security_group.traffic_ssh.id
  ]

  user_data = <<-EOT
    #!/bin/bash

    # Agregar segunda llave SSH al usuario ec2-user
    echo "${local.ssh_public_keys[1]}" >> /home/ec2-user/.ssh/authorized_keys
    chown ec2-user:ec2-user /home/ec2-user/.ssh/authorized_keys
    chmod 600 /home/ec2-user/.ssh/authorized_keys

    # Variables de entorno
    export DATABASE_HOST=${aws_instance.database.private_ip}
    export MONGODB_HOST=${aws_instance.mongodb.private_ip}
    export REPORTES_SERVICE_URL=http://${aws_instance.servicio_reportes.private_ip}:8000
    
    echo "DATABASE_HOST=${aws_instance.database.private_ip}" >> /etc/environment
    echo "MONGODB_HOST=${aws_instance.mongodb.private_ip}" >> /etc/environment
    echo "REPORTES_SERVICE_URL=http://${aws_instance.servicio_reportes.private_ip}:8000" >> /etc/environment

    sudo dnf install nano git docker -y
    sudo systemctl enable docker
    sudo systemctl start docker

    mkdir -p /proyecto
    cd /proyecto

    if [ ! -d Provesi ]; then
      git clone ${local.repository} Provesi
    fi

    cd Provesi

    # Configurar IPs en Dockerfile
    sudo sed -i "s/<DATABASE_HOST>/${aws_instance.database.private_ip}/g" manejador_pedidos/Dockerfile
    sudo sed -i "s/<MONGODB_HOST>/${aws_instance.mongodb.private_ip}/g" manejador_pedidos/Dockerfile

    docker build \
      -t manejador-pedidos-app \
      -f manejador_pedidos/Dockerfile \
      .

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

# ---------- EC2 - Manejador Inventario (a, b) ----------

resource "aws_instance" "manejador_inventario" {
  for_each = toset(["a", "b"])

  ami                         = "ami-051685736c7b35f95"
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.provesi_team.key_name
  associate_public_ip_address = true
  vpc_security_group_ids      = [
    aws_security_group.traffic_django.id,
    aws_security_group.traffic_ssh.id
  ]

  user_data = <<-EOT
    #!/bin/bash

    # Agregar segunda llave SSH al usuario ec2-user
    echo "${local.ssh_public_keys[1]}" >> /home/ec2-user/.ssh/authorized_keys
    chown ec2-user:ec2-user /home/ec2-user/.ssh/authorized_keys
    chmod 600 /home/ec2-user/.ssh/authorized_keys

    # Variables de entorno
    export DATABASE_HOST=${aws_instance.database.private_ip}
    export MONGODB_HOST=${aws_instance.mongodb.private_ip}
    export REPORTES_SERVICE_URL=http://${aws_instance.servicio_reportes.private_ip}:8000
    
    echo "DATABASE_HOST=${aws_instance.database.private_ip}" >> /etc/environment
    echo "MONGODB_HOST=${aws_instance.mongodb.private_ip}" >> /etc/environment
    echo "REPORTES_SERVICE_URL=http://${aws_instance.servicio_reportes.private_ip}:8000" >> /etc/environment

    sudo dnf install nano git docker -y
    sudo systemctl enable docker
    sudo systemctl start docker

    mkdir -p /proyecto
    cd /proyecto

    if [ ! -d Provesi ]; then
      git clone ${local.repository} Provesi
    fi

    cd Provesi

    # Configurar IPs en Dockerfile
    sudo sed -i "s/<DATABASE_HOST>/${aws_instance.database.private_ip}/g" manejador_inventario/Dockerfile
    sudo sed -i "s/<MONGODB_HOST>/${aws_instance.mongodb.private_ip}/g" manejador_inventario/Dockerfile

    docker build \
      -t manejador-inventario-app \
      -f manejador_inventario/Dockerfile \
      .

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

# ---------- EC2 - Kong API Gateway ----------

resource "aws_instance" "kong" {
  ami                         = "ami-051685736c7b35f95"
  instance_type               = var.instance_type
  key_name                    = aws_key_pair.provesi_team.key_name
  associate_public_ip_address = true
  vpc_security_group_ids      = [
    aws_security_group.traffic_app.id,
    aws_security_group.traffic_ssh.id
  ]

  user_data = <<-EOT
    #!/bin/bash
    # NO usar set -e aquí porque queremos que Kong se inicie incluso si algunos checks fallan
    
    # Logging mejorado
    exec > >(tee /var/log/user-data.log)
    exec 2>&1

    echo "======================================"
    echo "🔑 Configurando llaves SSH"
    echo "======================================"

    # Agregar segunda llave SSH al usuario ec2-user
    echo "${local.ssh_public_keys[1]}" >> /home/ec2-user/.ssh/authorized_keys
    chown ec2-user:ec2-user /home/ec2-user/.ssh/authorized_keys
    chmod 600 /home/ec2-user/.ssh/authorized_keys

    echo "======================================"
    echo "📦 Instalando dependencias"
    echo "======================================"

    sudo dnf install -y nano git docker nc
    sudo systemctl enable docker
    sudo systemctl start docker

    # Esperar a que Docker esté listo
    sleep 5

    echo "======================================"
    echo "📁 Clonando repositorio"
    echo "======================================"

    sudo mkdir -p /proyecto
    cd /proyecto
    
    if [ ! -d "Provesi" ]; then
      sudo git clone ${local.repository}
    fi
    
    cd Provesi

    echo "======================================"
    echo "⏳ Esperando instancias Django..."
    echo "======================================"

    # Función para verificar si una IP responde
    wait_for_instance() {
      local ip=$1
      local max_attempts=30
      local attempt=0
      
      echo "Esperando a que $ip:8080 esté disponible..."
      
      while [ $attempt -lt $max_attempts ]; do
        if nc -z -w5 $ip 8080 2>/dev/null; then
          echo "✅ $ip:8080 está disponible"
          return 0
        fi
        attempt=$((attempt + 1))
        echo "  Intento $attempt/$max_attempts..."
        sleep 10
      done
      
      echo "⚠️ Timeout esperando $ip (continuando de todas formas)"
      return 0  # No fallar, continuar con el deployment
    }

    # Esperar a que las instancias Django estén disponibles (best effort)
    wait_for_instance ${aws_instance.manejador_pedidos["a"].private_ip}
    wait_for_instance ${aws_instance.manejador_inventario["a"].private_ip}

    echo "======================================"
    echo "⚙️ Configurando Kong"
    echo "======================================"

    # Backup del archivo original
    cp kong.yml kong.yml.bak

    # Insert IPs into kong.yml
    sed -i "s/<PEDIDOS_A_HOST>/${aws_instance.manejador_pedidos["a"].private_ip}/g" kong.yml
    sed -i "s/<PEDIDOS_B_HOST>/${aws_instance.manejador_pedidos["b"].private_ip}/g" kong.yml
    sed -i "s/<PEDIDOS_C_HOST>/${aws_instance.manejador_pedidos["c"].private_ip}/g" kong.yml

    sed -i "s/<INVENTARIO_A_HOST>/${aws_instance.manejador_inventario["a"].private_ip}/g" kong.yml
    sed -i "s/<INVENTARIO_B_HOST>/${aws_instance.manejador_inventario["b"].private_ip}/g" kong.yml

    # Verificar que las IPs se reemplazaron
    echo "Contenido de kong.yml después de sed:"
    cat kong.yml | grep -A5 "targets:"

    echo "======================================"
    echo "🐳 Iniciando Kong"
    echo "======================================"

    # Crear red de Docker
    docker network create kong-network 2>/dev/null || true
    
    # Ejecutar Kong
    docker run -d \
      --name kong \
      --network=kong-network \
      --restart=always \
      -v "$(pwd):/kong/declarative/" \
      -e "KONG_DATABASE=off" \
      -e "KONG_DECLARATIVE_CONFIG=/kong/declarative/kong.yml" \
      -e "KONG_LOG_LEVEL=debug" \
      -p 8000:8000 \
      kong/kong-gateway

    echo ""
    echo "======================================"
    echo "✅ Kong desplegado"
    echo "======================================"
    echo "Kong Gateway: http://$(hostname -I | awk '{print $1}'):8000"
    
    # Esperar y verificar que Kong está corriendo
    sleep 15
    
    if docker ps | grep kong; then
      echo "✅ Kong está corriendo correctamente"
      docker logs kong --tail 20
    else
      echo "❌ Kong no está corriendo"
      docker logs kong || true
      exit 1
    fi

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

# ---------- EC2 - Manejador de busquedas ----------

resource "aws_instance" "manejador_busquedas" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  associate_public_ip_address = true

  vpc_security_group_ids = [
    aws_security_group.traffic_app.id,
    aws_security_group.traffic_ssh.id
  ]

  depends_on = [aws_instance.mongodb]

  user_data = <<-EOT
    #!/bin/bash
    set -e
    exec > >(tee /var/log/user-data.log) 2>&1

    echo "✅ Configurando variable de entorno Mongo"
    echo "PROVESI_DB_HOST=${aws_instance.mongodb.public_ip}" | sudo tee -a /etc/environment
    source /etc/environment

    echo "✅ Instalando dependencias del sistema"
    sudo apt-get update -y
    sudo apt-get install -y python3-pip git python3-venv build-essential

    echo "✅ Clonando repositorio"
    sudo mkdir -p /proyecto
    cd /proyecto
    sudo git clone https://github.com/ScrumTeam-2503/Manejador_busquedas.git Provesi
    cd Provesi

    echo "✅ Creando entorno virtual"
    python3 -m venv venv
    source venv/bin/activate

    echo "✅ Instalando requirements"
    pip install --upgrade pip
    pip install -r requirements.txt

    echo "✅ Creando servicio systemd para FastAPI"
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

    echo "✅ FastAPI corriendo automáticamente"
  EOT

  tags = merge(local.common_tags, {
    Name = "${var.project_prefix}-manejador-busquedas",
    Role = "manejador-busquedas"
  })
}

# ---------- Outputs ----------

output "ssh_connection_info" {
  value = <<-EOT
    ✅ SSH Keys configuradas exitosamente!
    
    Puedes conectarte a cualquier instancia usando:
    
    ssh -i ~/.ssh/tu_llave_privada ubuntu@<IP>    (para instancias Ubuntu)
    ssh -i ~/.ssh/tu_llave_privada ec2-user@<IP>  (para instancias Amazon Linux)
    
    Nota: Las llaves privadas correspondientes deben estar en tu máquina local.
  EOT
  description = "Información de conexión SSH"
}

output "kong_public_ip" {
  value       = aws_instance.kong.public_ip
  description = "IP pública de Kong API Gateway"
}

output "manejador_busquedas_public_ip" {
  value       = aws_instance.manejador_busquedas
  description = "IP pública del manejador de busquedas"
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
  description = "IP privada de MongoDB (usar en Django)"
}

output "mongodb_public_ip" {
  value       = aws_instance.mongodb.public_ip
  description = "IP pública de MongoDB (para SSH y debugging)"
}

output "mongodb_connection_string" {
  value       = "mongodb://provesi_user:scrumteam@${aws_instance.mongodb.private_ip}:27017/provesi_mongodb"
  description = "Connection string para MongoDB"
  sensitive   = true
}

output "servicio_reportes_public_ip" {
  value       = aws_instance.servicio_reportes.public_ip
  description = "IP pública del servicio de reportes"
}

output "servicio_reportes_private_ip" {
  value       = aws_instance.servicio_reportes.private_ip
  description = "IP privada del servicio de reportes (usar en Django)"
}

output "manejador_pedidos_public_ips" {
  value       = { for id, inst in aws_instance.manejador_pedidos : id => inst.public_ip }
  description = "IPs públicas de instancias de pedidos"
}

output "manejador_inventario_public_ips" {
  value       = { for id, inst in aws_instance.manejador_inventario : id => inst.public_ip }
  description = "IPs públicas de instancias de inventario"
}

output "manejador_pedidos_private_ips" {
  value       = { for id, inst in aws_instance.manejador_pedidos : id => inst.private_ip }
  description = "IPs privadas de instancias de pedidos"
}

output "manejador_inventario_private_ips" {
  value       = { for id, inst in aws_instance.manejador_inventario : id => inst.private_ip }
  description = "IPs privadas de instancias de inventario"
}

output "infrastructure_summary" {
  value = {
    kong = {
      public_ip = aws_instance.kong.public_ip
      ssh_user  = "ec2-user"
      endpoints = {
        pedidos    = "http://${aws_instance.kong.public_ip}:8000/manejador_pedidos/pedidos/"
        inventario = "http://${aws_instance.kong.public_ip}:8000/manejador_inventario/bodegas/"
        reportes   = "http://${aws_instance.kong.public_ip}:8000/reportes/"
      }
    }
    postgresql = {
      private_ip = aws_instance.database.private_ip
      public_ip  = aws_instance.database.public_ip
      ssh_user   = "ubuntu"
      connection = "postgresql://provesi_user:scrumteam@${aws_instance.database.private_ip}:5432/provesi_db"
    }
    mongodb = {
      private_ip = aws_instance.mongodb.private_ip
      public_ip  = aws_instance.mongodb.public_ip
      ssh_user   = "ubuntu"
      connection = "mongodb://provesi_user:scrumteam@${aws_instance.mongodb.private_ip}:27017/provesi_mongodb"
    }
    servicio_reportes = {
      private_ip   = aws_instance.servicio_reportes.private_ip
      public_ip    = aws_instance.servicio_reportes.public_ip
      ssh_user     = "ec2-user"
      health_check = "http://${aws_instance.servicio_reportes.public_ip}:8000/health"
      api_docs     = "http://${aws_instance.servicio_reportes.public_ip}:8000/docs"
      redoc        = "http://${aws_instance.servicio_reportes.public_ip}:8000/redoc"
    }
    django_instances = {
      pedidos = {
        a = {
          ip       = aws_instance.manejador_pedidos["a"].public_ip
          ssh_user = "ec2-user"
        }
        b = {
          ip       = aws_instance.manejador_pedidos["b"].public_ip
          ssh_user = "ec2-user"
        }
        c = {
          ip       = aws_instance.manejador_pedidos["c"].public_ip
          ssh_user = "ec2-user"
        }
      }
      inventario = {
        a = {
          ip       = aws_instance.manejador_inventario["a"].public_ip
          ssh_user = "ec2-user"
        }
        b = {
          ip       = aws_instance.manejador_inventario["b"].public_ip
          ssh_user = "ec2-user"
        }
      }
    }
  }
  description = "Resumen completo de la infraestructura"
}

output "quick_access_urls" {
  value = <<-EOT
    
    ╔════════════════════════════════════════════════════════════════╗
    ║          🚀 PROVESI WMS - INFRAESTRUCTURA DESPLEGADA          ║
    ╚════════════════════════════════════════════════════════════════╝
    
    📊 SERVICIO DE REPORTES:
       Health Check:   http://${aws_instance.servicio_reportes.public_ip}:8000/health
       API Docs:       http://${aws_instance.servicio_reportes.public_ip}:8000/docs
       Reportes:       http://${aws_instance.servicio_reportes.public_ip}:8000/reportes/inventario
    
    🌐 KONG API GATEWAY:
       Pedidos:        http://${aws_instance.kong.public_ip}:8000/manejador_pedidos/pedidos/
       Inventario:     http://${aws_instance.kong.public_ip}:8000/manejador_inventario/bodegas/
       Reportes:       http://${aws_instance.kong.public_ip}:8000/reportes/
    
    🗄️ BASES DE DATOS:
       PostgreSQL:     ${aws_instance.database.private_ip}:5432
       MongoDB:        ${aws_instance.mongodb.private_ip}:27017
    
    💡 Para SSH:
       ssh -i tu-llave.pem ec2-user@${aws_instance.servicio_reportes.public_ip}
    
    ╚════════════════════════════════════════════════════════════════╝
  EOT
  description = "URLs de acceso rápido"
}
