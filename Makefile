# Variables para facilitar cambios
VENV = vens2
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

.PHONY: start test clean run

# 1. Instala todo: crea el entorno si no existe y carga las librerías
start:
	@echo "--- Configurando el proyecto ---"
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creando entorno virtual $(VENV)..."; \
		python3 -m venv $(VENV); \
	fi
	@echo "Instalando/Actualizando dependencias desde requirements.txt..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "--- Todo listo. Usa 'make run' para iniciar o 'make test' ---"

# 2. Ejecuta los tests (asumiendo que usas pytest o unittest)
test:
	@echo "--- Ejecutando las pruebas ---"
	$(PYTHON) -m pytest test/

# 3. Comando extra para lanzar tu app.py
run:
	@echo "--- Iniciando isi-smartwatt ---"
	$(PYTHON) app.py

# 4. Limpieza de archivos basura de Python
clean:
	@echo "Limpiando archivos temporales..."
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Limpieza completada."