#!/usr/bin/env bash
set -euo pipefail

FLAG="$HOME/.openclaw/automejora/automejora_24_7.enabled"
LOG_DIR="$HOME/.openclaw/automejora/logs"
STATE="$HOME/.openclaw/automejora/state/update_progress.py"
BACKLOG="$HOME/.openclaw/automejora/backlog/tasks.json"

mkdir -p "$LOG_DIR"
mkdir -p "$(dirname "$BACKLOG")"
mkdir -p "$(dirname "$STATE")"

if [ ! -f "$BACKLOG" ]; then
cat > "$BACKLOG" <<'EOF'
[
  {
    "id": "01-revisar-pendientes",
    "titulo": "Revisar tareas pendientes anteriores",
    "estado": "pending",
    "prioridad": "alta"
  },
  {
    "id": "02-buscar-mejoras",
    "titulo": "Buscar mejoras posibles del sistema",
    "estado": "pending",
    "prioridad": "alta"
  },
  {
    "id": "03-buscar-skills",
    "titulo": "Buscar skills útiles para mejorar MoltBot/OpenClaw",
    "estado": "pending",
    "prioridad": "alta"
  },
  {
    "id": "04-revisar-integraciones",
    "titulo": "Comprobar Drive, Gmail y GitHub",
    "estado": "pending",
    "prioridad": "alta"
  }
]
EOF
fi

update_state() {
  local state="$1"
  local task="$2"
  local step="$3"
  local done="$4"
  local total="$5"
  local errors="$6"
  local auto="$7"

  python3 "$STATE" "$state" "$task" "$step" "$done" "$total" "$errors" "$auto" || true
}

while true; do
  if [ ! -f "$FLAG" ]; then
    update_state "done" "Automejora pausada" "Esperando activación desde la app móvil" 0 0 0 false
    sleep 10
    continue
  fi

  TOTAL=10
  DONE=0
  ERRORS=0
  LOG="$LOG_DIR/automejora_$(date +%F).log"

  {
    echo ""
    echo "===================================="
    echo "CICLO MOLTBOT: $(date)"
    echo "PC: $(hostname)"
    echo "===================================="

    update_state "working" "Revisando backlog" "Leyendo tareas pendientes" "$DONE" "$TOTAL" "$ERRORS" true
    echo ""
    echo "[1] Backlog actual"
    cat "$BACKLOG" || true
    DONE=$((DONE+1))

    update_state "working" "Buscando tareas que quedaron para luego" "Buscando palabras clave en ~/.openclaw" "$DONE" "$TOTAL" "$ERRORS" true
    echo ""
    echo "[2] Búsqueda de pendientes antiguos"
    grep -RinE "para luego|cuando acabes|pendiente|falta hacer|revisar luego|mejorar después|TODO|FIXME" "$HOME/.openclaw" 2>/dev/null | head -120 || true
    DONE=$((DONE+1))

    update_state "working" "Comprobando OpenClaw" "Ejecutando openclaw status --all" "$DONE" "$TOTAL" "$ERRORS" true
    echo ""
    echo "[3] Estado OpenClaw"
    openclaw status --all || true
    DONE=$((DONE+1))

    update_state "working" "Comprobando permisos root" "Ejecutando sudo -n whoami" "$DONE" "$TOTAL" "$ERRORS" true
    echo ""
    echo "[4] Sudo sin contraseña"
    sudo -n whoami || true
    DONE=$((DONE+1))

    update_state "working" "Revisando Tailscale y red" "Ejecutando tailscale status" "$DONE" "$TOTAL" "$ERRORS" true
    echo ""
    echo "[5] Tailscale"
    tailscale ip -4 || true
    tailscale status || true
    DONE=$((DONE+1))

    update_state "working" "Analizando logs" "Leyendo journalctl de usuario" "$DONE" "$TOTAL" "$ERRORS" true
    echo ""
    echo "[6] Logs systemd user"
    journalctl --user -n 160 --no-pager || true
    DONE=$((DONE+1))

    update_state "working" "Buscando errores del sistema" "Revisando servicios fallidos, disco y RAM" "$DONE" "$TOTAL" "$ERRORS" true
    echo ""
    echo "[7] Sistema"
    systemctl --user --failed || true
    df -h || true
    free -h || true
    uptime || true
    DONE=$((DONE+1))

    update_state "working" "Comprobando integraciones" "Drive, Gmail y GitHub" "$DONE" "$TOTAL" "$ERRORS" true
    echo ""
    echo "[8] Integraciones"
    if [ -f "$HOME/.openclaw/integrations/google_credentials.json" ]; then
      echo "Google credentials: OK"
    else
      echo "Google credentials: PENDIENTE"
    fi

    if [ -f "$HOME/.openclaw/integrations/google_token.json" ]; then
      echo "Google token Drive/Gmail: OK"
    else
      echo "Google token Drive/Gmail: PENDIENTE"
    fi

    if [ -f "$HOME/.openclaw/integrations/github_token.txt" ]; then
      echo "GitHub token: OK"
    else
      echo "GitHub token: PENDIENTE"
    fi
    DONE=$((DONE+1))

    update_state "working" "Buscando mejoras posibles" "Generando lista de mejoras candidatas" "$DONE" "$TOTAL" "$ERRORS" true
    echo ""
    echo "[9] Mejoras candidatas"
    echo "- Skill de backup automático a Drive"
    echo "- Skill de lectura/resumen de Gmail"
    echo "- Skill de gestión de repos GitHub"
    echo "- Skill de recuperación automática de servicios caídos"
    echo "- Skill de limpieza de logs antiguos"
    echo "- Skill de diagnóstico de red/Tailscale"
    echo "- Skill de test automático de proyectos"
    echo "- Skill de reporte diario al móvil"
    DONE=$((DONE+1))

    update_state "working" "Cerrando ciclo" "Guardando resultado del ciclo" "$DONE" "$TOTAL" "$ERRORS" true
    echo ""
    echo "[10] Ciclo terminado correctamente"
    echo "Fecha fin: $(date)"
    DONE=$((DONE+1))

    update_state "done" "Ciclo de automejora completado" "Esperando siguiente ciclo" "$DONE" "$TOTAL" "$ERRORS" true

  } >> "$LOG" 2>&1 || {
    ERRORS=$((ERRORS+1))
    update_state "error" "Error en automejora" "Revisar log: $LOG" "$DONE" "$TOTAL" "$ERRORS" true
  }

  sleep 300
done