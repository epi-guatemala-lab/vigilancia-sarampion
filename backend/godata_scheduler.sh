#!/bin/bash
# GoData Scheduled Batch Sync
# Cron: 0 10 * * 1-5  (10am Lun-Vie, 1 hora después del MSPAS scheduler)
# Sincroniza TODOS los registros aprobados con GoData en una sola llamada API
#
# SEGURIDAD: Solo sincroniza realmente si GODATA_PRODUCTION_MODE=true en systemd env
# En modo prueba, genera payloads pero NO los envía a GoData

BACKEND="/opt/vigilancia-sarampion/backend"
VENV="/opt/vigilancia-sarampion/venv/bin/python3"
LOG="/var/log/igss-godata-scheduler.log"
API_URL="http://localhost:8510/api"
API_KEY=$(grep API_SECRET $BACKEND/.env | cut -d= -f2 | tr -d '"' | tr -d "'")

echo "$(date '+%Y-%m-%d %H:%M:%S') — GoData batch scheduler started" >> $LOG

# 1. Count approved records
APPROVED=$(curl -s -H "X-Api-Key: $API_KEY" "$API_URL/godata/queue?estado=aprobado&limit=0" 2>/dev/null | \
  $VENV -c "import json,sys; d=json.load(sys.stdin); print(d.get('counts',{}).get('aprobado',0))" 2>/dev/null)
echo "$(date '+%Y-%m-%d %H:%M:%S') — Approved records for GoData: $APPROVED" >> $LOG

if [ "$APPROVED" = "0" ] || [ -z "$APPROVED" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') — No approved records for GoData. Done." >> $LOG
    exit 0
fi

# 2. Sync ALL approved records in a single batch call
# Timeout: 1 hour (GoData API is faster than Playwright bot)
echo "$(date '+%Y-%m-%d %H:%M:%S') — Starting GoData batch sync of $APPROVED records..." >> $LOG
RESULT=$(curl -s --max-time 3600 -X POST -H "X-Api-Key: $API_KEY" "$API_URL/godata/sync-batch" 2>/dev/null)

# 3. Log result
echo "$(date '+%Y-%m-%d %H:%M:%S') — GoData batch result: $RESULT" >> $LOG

# Extract counts for summary
PROCESSED=$($VENV -c "import json,sys; print(json.load(sys.stdin).get('processed',0))" <<< "$RESULT" 2>/dev/null)
SUCCESS=$($VENV -c "import json,sys; print(json.load(sys.stdin).get('success',0))" <<< "$RESULT" 2>/dev/null)
ERRORS=$($VENV -c "import json,sys; print(json.load(sys.stdin).get('errors',0))" <<< "$RESULT" 2>/dev/null)
DUPES=$($VENV -c "import json,sys; print(json.load(sys.stdin).get('duplicates',0))" <<< "$RESULT" 2>/dev/null)

echo "$(date '+%Y-%m-%d %H:%M:%S') — Done: $PROCESSED processed, $SUCCESS ok, $ERRORS errors, $DUPES duplicates" >> $LOG
