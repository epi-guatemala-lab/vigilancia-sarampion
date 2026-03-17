#!/bin/bash
# Deploy del backend de Vigilancia Sarampión en el servidor igss.mediclic.org
# Ejecutar desde el servidor: bash deploy.sh

set -e

APP_DIR="/opt/vigilancia-sarampion"
SERVICE_NAME="vigilancia-sarampion"

echo "=== Deploy Vigilancia Sarampión API ==="

# Crear directorio
sudo mkdir -p $APP_DIR/data
sudo chown -R $USER:$USER $APP_DIR

# Copiar archivos
cp main.py config.py database.py requirements.txt $APP_DIR/

# Entorno virtual
if [ ! -d "$APP_DIR/venv" ]; then
    python3 -m venv $APP_DIR/venv
fi
source $APP_DIR/venv/bin/activate
pip install -r $APP_DIR/requirements.txt --quiet

# Copiar .env si no existe
if [ ! -f "$APP_DIR/.env" ]; then
    cp .env.example $APP_DIR/.env
    echo "⚠️  Editar $APP_DIR/.env con las credenciales correctas"
fi

# Crear servicio systemd
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << EOF
[Unit]
Description=Vigilancia Sarampion API - IGSS
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8502
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo "=== Servicio activo en puerto 8502 ==="
echo "Agregar a nginx:"
echo ""
echo "  location /sarampion/ {"
echo "      proxy_pass http://127.0.0.1:8502/;"
echo "      proxy_set_header Host \$host;"
echo "      proxy_set_header X-Real-IP \$remote_addr;"
echo "      proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;"
echo "  }"
echo ""
echo "Luego: sudo nginx -t && sudo systemctl reload nginx"

systemctl status $SERVICE_NAME --no-pager
