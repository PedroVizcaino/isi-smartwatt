# Intentar detectar si usar 'docker compose' (v2) o 'docker-compose' (v1)
DOCKER_COMPOSE := $(shell command -v docker-compose 2> /dev/null || echo "docker compose")

.PHONY: start run stop restart clean logs status help

# Ayuda por defecto
help:
	@echo "SmartWatt - Gestión del Proyecto"
	@echo ""
	@echo "Comandos disponibles:"
	@echo "  make install - Instala Docker y Docker Compose en el sistema"
	@echo "  make start   - Construye las imágenes de Docker (Primer paso)"
	@echo "  make run     - Levanta todos los servicios (App, DB, IA)"
	@echo "  make stop    - Detiene todos los servicios"
	@echo "  make restart - Reinicia los servicios"
	@echo "  make logs    - Muestra los logs en tiempo real"
	@echo "  make status  - Muestra el estado de los contenedores"
	@echo "  make clean   - Limpia contenedores, imágenes y volúmenes"
	@echo ""

# 0. Instala Docker (Pre-requisito)
install:
	@echo "--- Instalando Docker y Docker Compose ---"
	sudo apt update
	sudo apt install -y docker.io docker-compose-v2
	@echo "--- Instalación completada ---"

# 1. Instala lo necesario (Construye las imágenes)
start:
	@$(DOCKER_COMPOSE) version > /dev/null 2>&1 || (echo "⚠ Docker no detectado. Iniciando instalación..." && $(MAKE) install)
	@echo "--- Preparando SmartWatt (Docker) ---"
	$(DOCKER_COMPOSE) build
	@echo "--- Construcción completada. Usa 'make run' para iniciar ---"

# 2. Ejecuta la aplicación
run:
	@$(DOCKER_COMPOSE) version > /dev/null 2>&1 || (echo "⚠ Docker no detectado. Iniciando instalación..." && $(MAKE) install)
	@echo "--- Iniciando SmartWatt (Modo Detached) ---"
	$(DOCKER_COMPOSE) up -d --build
	@echo ""
	@echo "🚀 SmartWatt está funcionando en:"
	@echo "👉 Frontend: http://localhost"
	@echo "👉 Backend API: http://localhost:5000"
	@echo ""
	@echo "Nota: El modelo de IA se descargará automáticamente en segundo plano."
	@echo "Usa 'make logs' para ver el progreso."

# 3. Detiene los servicios
stop:
	@echo "--- Deteniendo servicios ---"
	$(DOCKER_COMPOSE) stop

# 4. Reinicia los servicios
restart:
	@echo "--- Reiniciando servicios ---"
	$(DOCKER_COMPOSE) restart

# 5. Muestra logs
logs:
	$(DOCKER_COMPOSE) logs -f

# 6. Estado de los servicios
status:
	$(DOCKER_COMPOSE) ps

# 7. Limpieza profunda
clean:
	@echo "--- Limpiando entorno Docker ---"
	$(DOCKER_COMPOSE) down --rmi all --volumes --remove-orphans
	@echo "--- Limpieza completada ---"