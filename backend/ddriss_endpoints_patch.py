
# ─── DDRISS Reporting ───────────────────────────────────────

@app.get("/api/reportes/ddriss-list")
def reporte_ddriss_list(x_api_key: str = Header(None)):
    """Get the list of all DDRISS names."""
    verify_api_key(x_api_key)
    from ddriss_mapping import DDRISS_LIST
    return {"ddriss": DDRISS_LIST}


@app.get("/api/reportes/ddriss-counts")
def reporte_ddriss_counts(
    fecha_inicio: str = None,
    fecha_fin: str = None,
    x_api_key: str = Header(None),
):
    """Get count of records per DDRISS, optionally filtered by date range."""
    verify_api_key(x_api_key)
    from ddriss_mapping import get_ddriss, DDRISS_LIST
    from database import get_connection

    conn = get_connection()
    try:
        params = []
        query = "SELECT departamento_residencia, municipio_residencia FROM registros WHERE 1=1"
        if fecha_inicio:
            query += " AND fecha_notificacion >= ?"
            params.append(fecha_inicio)
        if fecha_fin:
            query += " AND fecha_notificacion <= ?"
            params.append(fecha_fin)

        rows = conn.execute(query, params).fetchall()

        counts = {d: 0 for d in DDRISS_LIST}
        for row in rows:
            ddriss = get_ddriss(row['departamento_residencia'] or '', row['municipio_residencia'] or '')
            if ddriss in counts:
                counts[ddriss] += 1
            else:
                counts[ddriss] = counts.get(ddriss, 0) + 1

        # Sort by count descending, then name
        sorted_counts = dict(sorted(counts.items(), key=lambda x: (-x[1], x[0])))
        return {"counts": sorted_counts, "total": len(rows)}
    finally:
        conn.close()


@app.post("/api/reportes/fichas-por-ddriss")
async def reporte_fichas_por_ddriss(request: Request, x_api_key: str = Header(None)):
    """Generate bulk fichas filtered by DDRISS and date range.
    Body: {"ddriss": "GUATEMALA SUR", "fecha_inicio": "2026-01-01", "fecha_fin": "2026-03-31", "format": "merged"|"zip"}
    """
    verify_api_key(x_api_key)
    body = await request.json()
    ddriss = body.get("ddriss", "").strip()
    fecha_inicio = body.get("fecha_inicio", "")
    fecha_fin = body.get("fecha_fin", "")
    fmt = body.get("format", "merged")

    if not ddriss:
        raise HTTPException(400, "Debe seleccionar un DDRISS")

    from ddriss_mapping import get_ddriss
    from database import get_connection

    conn = get_connection()
    try:
        params = []
        query = "SELECT * FROM registros WHERE 1=1"
        if fecha_inicio:
            query += " AND fecha_notificacion >= ?"
            params.append(fecha_inicio)
        if fecha_fin:
            query += " AND fecha_notificacion <= ?"
            params.append(fecha_fin)

        rows = conn.execute(query, params).fetchall()

        # Filter by DDRISS
        records = []
        for row in rows:
            r = dict(row)
            record_ddriss = get_ddriss(
                r.get('departamento_residencia', ''),
                r.get('municipio_residencia', '')
            )
            if record_ddriss == ddriss:
                records.append(r)

        if not records:
            raise HTTPException(404, f"No se encontraron registros para {ddriss} en el rango de fechas indicado")

        from pdf_ficha_v2 import generar_fichas_v2_bulk
        merge = (fmt == "merged")
        result_bytes = generar_fichas_v2_bulk(records, merge=merge)

        ext = "pdf" if merge else "zip"
        mime = "application/pdf" if merge else "application/zip"
        safe_name = ddriss.replace(' ', '_')
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"fichas_{safe_name}_{ts}.{ext}"

        return StreamingResponse(
            io.BytesIO(result_bytes),
            media_type=mime,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    finally:
        conn.close()

