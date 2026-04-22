/**
 * Hook para cargar unidades médicas del backend de forma dinámica.
 *
 * - GET /api/unidades/public  → lista de unidades ACTIVAS (source of truth en DB)
 * - Cache en localStorage (24h)
 * - Fallback inmediato a lista estática mientras fetch está pendiente / falla
 * - Re-fetch en background aunque haya cache (stale-while-revalidate)
 *
 * Cualquier unidad creada/desactivada desde el módulo admin se refleja en el
 * form en <5min (TTL del cache nginx + TTL localStorage).
 */
import { useEffect, useRef, useState } from 'react'
import { unidadesMedicas as STATIC_UNIDADES } from '../config/unidadesMedicas.js'

const STORAGE_KEY = 'igss_unidades_public_v1'
const CACHE_TTL_MS = 24 * 60 * 60 * 1000   // 24h
const API_URL_DEFAULT = '/sarampion/api/unidades/public'

function _readCache() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const { ts, data } = JSON.parse(raw)
    if (!ts || !data) return null
    if (Date.now() - ts > CACHE_TTL_MS) return null
    return data
  } catch {
    return null
  }
}

function _writeCache(data) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ ts: Date.now(), data }))
  } catch {
    // localStorage full, quota, etc. → silencioso
  }
}

function _normalizeFromApi(raw) {
  // La API responde {data: [{codigo, nombre, departamento, tipo}, ...]}
  // El form espera [{nombre, departamento}]
  const list = Array.isArray(raw?.data) ? raw.data : []
  return list.map((u) => ({
    nombre: u.nombre,
    departamento: u.departamento,
    codigo: u.codigo,
    tipo: u.tipo,
  }))
}

/**
 * Hook principal.
 *
 * @param {object} opts
 * @param {string} opts.apiUrl  URL del endpoint público (override de VITE_API_URL).
 * @returns {{unidades: Array, loading: boolean, error: Error|null, source: 'static'|'cache'|'api'}}
 */
export function useUnidadesPublic(opts = {}) {
  const apiUrl = opts.apiUrl || (import.meta?.env?.VITE_API_URL
    ? `${import.meta.env.VITE_API_URL}/api/unidades/public`.replace(/\/+/g, '/').replace(':/', '://')
    : API_URL_DEFAULT)

  // Inicial: cache si existe, sino estático
  const cached = _readCache()
  const [state, setState] = useState({
    unidades: cached || STATIC_UNIDADES,
    loading: cached ? false : true,
    error: null,
    source: cached ? 'cache' : 'static',
  })

  const fetchedOnce = useRef(false)

  useEffect(() => {
    // stale-while-revalidate: siempre re-fetch en background
    if (fetchedOnce.current) return
    fetchedOnce.current = true

    let aborted = false
    const ac = new AbortController()

    ;(async () => {
      try {
        const r = await fetch(apiUrl, { signal: ac.signal })
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        const j = await r.json()
        const normalized = _normalizeFromApi(j)
        if (normalized.length === 0) throw new Error('Respuesta vacía')
        if (aborted) return
        _writeCache(normalized)
        setState({
          unidades: normalized,
          loading: false,
          error: null,
          source: 'api',
        })
      } catch (e) {
        if (aborted) return
        // No romper la UI — mantiene la lista actual (cache o estática)
        console.warn('[useUnidadesPublic] fetch falló, usando fallback:', e.message)
        setState((s) => ({ ...s, loading: false, error: e }))
      }
    })()

    return () => {
      aborted = true
      ac.abort()
    }
  }, [apiUrl])

  return state
}

/**
 * Helper: solo los nombres (para options de dropdown).
 */
export function useUnidadesNombres(opts = {}) {
  const { unidades, loading, error, source } = useUnidadesPublic(opts)
  return {
    nombres: unidades.map((u) => u.nombre),
    unidades,
    loading,
    error,
    source,
  }
}
