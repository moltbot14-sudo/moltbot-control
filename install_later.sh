#!/usr/bin/env bash
set -euo pipefail

echo "===================================="
echo "      MOLTBOT INSTALLER UBUNTU"
echo "===================================="

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_NAME="$(whoami)"
HOST_NAME="$(hostname)"

echo "[INFO] Usuario: $USER_NAME"
echo "[INFO] Hostname: $HOST_NAME"
echo "[INFO] Repo: $REPO_DIR"

echo ""
echo "[1/12] Instalando dependencias base..."
sudo apt update
sudo apt install -y \
  openssh-server \
  curl \
  git \
  python3 \
  python3-venv \
  python3-pip \
  autossh \
  jq

echo ""
echo "[2/12] Activando SSH..."
sudo systemctl enable --now ssh

echo ""
echo "[3/12] Instalando Tailscale si no existe..."
if ! command -v tailscale >/dev/null 2>&1; then
  curl -fsSL https://tailscale.com/install.sh | sh
else
  echo "[OK] Tailscale ya está instalado."
fi

echo ""
echo "[4/12] Conectando Tailscale..."
echo "Si aparece un enlace, ábrelo e inicia sesión."
sudo tailscale up --ssh || true

echo ""
echo "[5/12] Elevando permisos del usuario actual..."
echo "$USER_NAME ALL=(ALL:ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/99-openclaw-full-control >/dev/null
sudo chmod 440 /etc/sudoers.d/99-openclaw-full-control
sudo visudo -cf /etc/sudoers.d/99-openclaw-full-control

echo ""
echo "[6/12] Probando sudo sin contraseña..."
sudo -k
ROOT_TEST="$(sudo -n whoami)"
if [ "$ROOT_TEST" = "root" ]; then
  echo "[OK] Sudo sin contraseña funciona."
else
  echo "[ERROR] Sudo sin contraseña no funciona."
  exit 1
fi

echo ""
echo "[7/12] Activando linger para servicios de usuario..."
sudo loginctl enable-linger "$USER_NAME" || true

echo ""
echo "[8/12] Creando carpetas de MoltBot/OpenClaw..."
mkdir -p "$HOME/.openclaw/mobile_panel"
mkdir -p "$HOME/.openclaw/automejora/logs"
mkdir -p "$HOME/.openclaw/automejora/state"
mkdir -p "$HOME/.openclaw/automejora/backlog"
mkdir -p "$HOME/.openclaw/integrations"
mkdir -p "$HOME/.openclaw/prompts"

echo ""
echo "[9/12] Copiando prompts si existen..."
if [ -d "$REPO_DIR/prompts" ]; then
  cp -f "$REPO_DIR/prompts/"*.txt "$HOME/.openclaw/prompts/" 2>/dev/null || true
fi

echo ""
echo "[10/12] Creando estado base..."

cat > "$HOME/.openclaw/automejora/state/progress.json" <<EOF
{
  "pc": "$HOST_NAME",
  "state": "done",
  "percent": 0,
  "current_task": "Instalación base completada",
  "current_step": "Esperando activación de automejora",
  "cycle_id": "",
  "tasks_total": 0,
  "tasks_done": 0,
  "tasks_error": 0,
  "last_update": "$(date '+%Y-%m-%d %H:%M:%S')",
  "automejora_24_7": false
}
EOF

cat > "$HOME/.openclaw/automejora/state/history.json" <<EOF
[
  {
    "time": "$(date '+%Y-%m-%d %H:%M:%S')",
    "state": "done",
    "task": "Instalación base",
    "step": "Sistema preparado",
    "percent": 100
  }
]
EOF

cat > "$HOME/.openclaw/automejora/backlog/tasks.json" <<'EOF'
[
  {
    "id": "01-elevar-permisos",
    "titulo": "Elevar permisos de OpenClaw con sudo sin contraseña",
    "estado": "done",
    "prioridad": "alta"
  },
  {
    "id": "02-conectar-tailscale",
    "titulo": "Conectar Ubuntu a Tailscale",
    "estado": "pending",
    "prioridad": "alta"
  },
  {
    "id": "03-ssh-cruzado",
    "titulo": "Configurar SSH cruzado entre ambos PCs",
    "estado": "pending",
    "prioridad": "alta"
  },
  {
    "id": "04-app-movil",
    "titulo": "Instalar app móvil PWA con luces, progreso, tarea actual e historial",
    "estado": "pending",
    "prioridad": "alta"
  },
  {
    "id": "05-automejora-24-7",
    "titulo": "Activar automejora continua 24/7",
    "estado": "pending",
    "prioridad": "alta"
  },
  {
    "id": "06-drive-gmail-github",
    "titulo": "Conectar Drive, Gmail y GitHub con moltbot14@gmail.com",
    "estado": "pending",
    "prioridad": "alta"
  },
  {
    "id": "07-skills",
    "titulo": "Buscar skills útiles para mejorar mucho el sistema",
    "estado": "pending",
    "prioridad": "media"
  }
]
EOF

echo ""
echo "[11/12] Preparando entorno Python del panel móvil..."
if [ -f "$REPO_DIR/mobile_panel/requirements.txt" ]; then
  cd "$HOME/.openclaw/mobile_panel"
  python3 -m venv .venv
  .venv/bin/pip install --upgrade pip
  .venv/bin/pip install -r "$REPO_DIR/mobile_panel/requirements.txt"
else
  echo "[WARN] No existe mobile_panel/requirements.txt"
fi

echo ""
echo "[12/12] Reiniciando OpenClaw Gateway si existe..."
openclaw gateway restart 2>/dev/null || systemctl --user restart openclaw-gateway.service 2>/dev/null || true

echo ""
echo "===================================="
echo "        INSTALACIÓN TERMINADA"
echo "===================================="
echo "USUARIO: $(whoami)"
echo "HOSTNAME: $(hostname)"
echo "SUDO:"
sudo -n whoami || true
echo ""
echo "TAILSCALE IP:"
tailscale ip -4 || true
echo ""
echo "OPENCLAW:"
openclaw status --all || true
echo ""
echo "Siguiente paso:"
echo "1. Guardar la IP Tailscale."
echo "2. Repetir en el otro Ubuntu."
echo "3. Configurar SSH cruzado."
echo "4. Instalar el panel móvil avanzado."