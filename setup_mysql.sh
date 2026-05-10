#!/bin/bash

echo "========================================="
echo "Setup MySQL para ISI-SmartWatt"
echo "========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar si MySQL está instalado
check_mysql() {
    if command -v mysql &> /dev/null; then
        echo -e "${GREEN}✓ MySQL está instalado${NC}"
        mysql --version
        return 0
    else
        echo -e "${RED}✗ MySQL no está instalado${NC}"
        echo -e "${YELLOW}Instalando MySQL...${NC}"
        sudo apt update
        sudo apt install -y mysql-server
        return $?
    fi
}

# Verificar instalación
echo "1. Verificando MySQL..."
check_mysql

echo ""
echo "2. Creando base de datos y usuario..."
sudo mysql << 'SQL'
-- Crear base de datos
CREATE DATABASE IF NOT EXISTS smartwatt_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear usuario
CREATE USER IF NOT EXISTS 'smartwatt_user'@'localhost' IDENTIFIED BY 'smartwatt_pass';

-- Otorgar privilegios
GRANT ALL PRIVILEGES ON smartwatt_db.* TO 'smartwatt_user'@'localhost';
FLUSH PRIVILEGES;

-- Mostrar resultado
SELECT 'Base de datos y usuario creados correctamente' AS Status;
SQL

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Base de datos y usuario creados${NC}"
else
    echo -e "${RED}✗ Error creando base de datos${NC}"
    exit 1
fi

echo ""
echo "3. Importando schema..."
sudo mysql smartwatt_db < schema_mysql.sql

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Schema importado correctamente${NC}"
else
    echo -e "${RED}✗ Error importando schema${NC}"
    exit 1
fi

echo ""
echo "4. Verificando tablas creadas..."
sudo mysql smartwatt_db -e "SHOW TABLES;"

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}✓ Setup completado exitosamente${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Credenciales de acceso:"
echo "  Base de datos: smartwatt_db"
echo "  Usuario: smartwatt_user"
echo "  Contraseña: smartwatt_pass"
echo ""
echo "Para probar la conexión, ejecuta:"
echo "  python3 test_mysql.py"
