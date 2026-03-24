#!/bin/bash
# MSPAS EPIWEB Scheduled Submission
# Cron: 0 9 * * 1-5  (9am Lun-Vie)
# Procesa registros aprobados uno por uno con el bot Playwright
#
# SEGURIDAD: Solo envía realmente si MSPAS_PRODUCTION_MODE=true en systemd env
# En modo prueba, llena formularios pero NO hace click en Guardar

BACKEND="/opt/vigilancia-sarampion/backend"
VENV="/opt/vigilancia-sarampion/venv/bin/python3"
LOG="/var/log/igss-mspas-scheduler.log"
API_URL="http://localhost:8510/api"
API_KEY=$(grep API_SECRET $BACKEND/.env | cut -d= -f2 | tr -d '"' | tr -d "'")
MAX_PER_RUN=20

echo "$(date '+%Y-%m-%d %H:%M:%S') — MSPAS scheduler started" >> $LOG

# 1. Recover stuck submissions
$VENV -c "
import sys; sys.path.insert(0, '$BACKEND')
from mspas_queue import recover_stuck_submissions
recovered = recover_stuck_submissions()
if recovered:
    print(f'Recovered {recovered} stuck submissions')
" >> $LOG 2>&1

# 2. Count approved
APPROVED=$(curl -s -H "X-Api-Key: $API_KEY" "$API_URL/mspas/queue?estado=aprobado&limit=0" 2>/dev/null | \
  $VENV -c "import json,sys; d=json.load(sys.stdin); print(d.get('counts',{}).get('aprobado',0))" 2>/dev/null)
echo "$(date '+%Y-%m-%d %H:%M:%S') — Approved: $APPROVED" >> $LOG

if [ "$APPROVED" = "0" ] || [ -z "$APPROVED" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') — No approved records. Done." >> $LOG
    exit 0
fi

# 3. Get approved IDs (max per run)
RECORDS=$( curl -s -H "X-Api-Key: $API_KEY" "$API_URL/mspas/queue?estado=aprobado&limit=$MAX_PER_RUN" 2>/dev/null | \
  $VENV -c "import json,sys; [print(i['registro_id']) for i in json.load(sys.stdin).get('data',[])]" 2>/dev/null )

# 4. Process each
SUCCESS=0
ERRORS=0
for RID in $RECORDS; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') — Submitting: $RID" >> $LOG

    RESULT=$(curl -s --max-time 180 -X POST -H "X-Api-Key: $API_KEY" "$API_URL/mspas/submit/$RID" 2>/dev/null)

    IS_OK=$($VENV -c "import json,sys; print(json.load(sys.stdin).get('success',False))" <<< "$RESULT" 2>/dev/null)

    if [ "$IS_OK" = "True" ]; then
        SUCCESS=$((SUCCESS + 1))
        echo "  OK" >> $LOG
    else
        ERRORS=$((ERRORS + 1))
        ERR=$($VENV -c "import json,sys; print('; '.join(json.load(sys.stdin).get('errors',['?'])))" <<< "$RESULT" 2>/dev/null)
        echo "  ERROR: $ERR" >> $LOG
    fi

    sleep 5
done

echo "$(date '+%Y-%m-%d %H:%M:%S') — Done: $SUCCESS ok, $ERRORS errors" >> $LOG
