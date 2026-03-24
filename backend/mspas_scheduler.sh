#!/bin/bash
# MSPAS EPIWEB Scheduled Batch Submission
# Cron: 0 9 * * 1-5  (9am Lun-Vie)
# Procesa TODOS los registros aprobados en una sola sesión de browser (batch mode)
#
# OPTIMIZATION: Uses /api/mspas/submit-batch instead of individual submissions.
# 1 login instead of N logins saves ~15s per record.
# For 1000 records: ~14h instead of ~18h.
#
# SEGURIDAD: Solo envía realmente si MSPAS_PRODUCTION_MODE=true en systemd env
# En modo prueba, llena formularios pero NO hace click en Guardar

BACKEND="/opt/vigilancia-sarampion/backend"
VENV="/opt/vigilancia-sarampion/venv/bin/python3"
LOG="/var/log/igss-mspas-scheduler.log"
API_URL="http://localhost:8510/api"
API_KEY=$(grep API_SECRET $BACKEND/.env | cut -d= -f2 | tr -d '"' | tr -d "'")

echo "$(date '+%Y-%m-%d %H:%M:%S') — MSPAS batch scheduler started" >> $LOG

# 1. Count approved records
APPROVED=$(curl -s -H "X-Api-Key: $API_KEY" "$API_URL/mspas/queue?estado=aprobado&limit=0" 2>/dev/null | \
  $VENV -c "import json,sys; d=json.load(sys.stdin); print(d.get('counts',{}).get('aprobado',0))" 2>/dev/null)
echo "$(date '+%Y-%m-%d %H:%M:%S') — Approved records: $APPROVED" >> $LOG

if [ "$APPROVED" = "0" ] || [ -z "$APPROVED" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') — No approved records. Done." >> $LOG
    exit 0
fi

# 2. Submit ALL approved records in a single batch (one browser session)
# Timeout: 24 hours (86400s) — processing 1000 records takes ~14 hours
echo "$(date '+%Y-%m-%d %H:%M:%S') — Starting batch submission of $APPROVED records..." >> $LOG
RESULT=$(curl -s --max-time 86400 -X POST -H "X-Api-Key: $API_KEY" "$API_URL/mspas/submit-batch" 2>/dev/null)

# 3. Log result
echo "$(date '+%Y-%m-%d %H:%M:%S') — Batch result: $RESULT" >> $LOG

# Extract counts for summary
PROCESSED=$($VENV -c "import json,sys; print(json.load(sys.stdin).get('processed',0))" <<< "$RESULT" 2>/dev/null)
SUCCESS=$($VENV -c "import json,sys; print(json.load(sys.stdin).get('success',0))" <<< "$RESULT" 2>/dev/null)
ERRORS=$($VENV -c "import json,sys; print(json.load(sys.stdin).get('errors',0))" <<< "$RESULT" 2>/dev/null)
DUPES=$($VENV -c "import json,sys; print(json.load(sys.stdin).get('duplicates',0))" <<< "$RESULT" 2>/dev/null)

echo "$(date '+%Y-%m-%d %H:%M:%S') — Done: $PROCESSED processed, $SUCCESS ok, $ERRORS errors, $DUPES duplicates" >> $LOG
