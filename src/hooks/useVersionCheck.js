import { useEffect, useRef } from 'react'

/**
 * Detecta un build nuevo desplegado (GitHub Pages) y recarga la pestaña de forma
 * NO disruptiva.
 *
 * Escenario objetivo: las unidades médicas dejan el formulario abierto en una
 * pestaña por horas y luego envían con el bundle VIEJO en caché (no hay service
 * worker que lo actualice). Eso hizo que, tras un deploy, siguieran llegando
 * envíos con campos ya retirados (incidente criterio_descarte, jul-2026).
 *
 * Cómo funciona: al arrancar guarda el hash del bundle actual (del <script> con
 * `assets/index-<hash>.js`). Cada `intervalMs` — y al recuperar foco/visibilidad —
 * baja `index.html` (no-store) y compara el hash referenciado. Si cambió, marca
 * una recarga PENDIENTE y la ejecuta SOLO cuando la pestaña está en segundo plano
 * (`document.hidden`), para no interrumpir jamás una captura activa. El borrador
 * se autoguarda en localStorage (`sarampion_form_data`), así que recargar no pierde
 * datos: al volver, la pestaña ya corre el formulario nuevo con el draft restaurado.
 */
export function useVersionCheck({ intervalMs = 5 * 60 * 1000 } = {}) {
  const bootHash = useRef(null)
  const pending = useRef(false)
  const reloaded = useRef(false)

  useEffect(() => {
    // En dev no hay bundle con hash (Vite sirve módulos sin hashear) → no aplica.
    if (import.meta.env.DEV) return

    const el = document.querySelector('script[type="module"][src*="/assets/index-"]')
    const m = el && el.getAttribute('src').match(/index-([A-Za-z0-9_-]+)\.js/)
    if (!m) return
    bootHash.current = m[1]

    const base = import.meta.env.BASE_URL || '/'

    const reloadIfHidden = () => {
      if (pending.current && document.hidden && !reloaded.current) {
        reloaded.current = true
        window.location.reload()
      }
    }

    const check = async () => {
      if (reloaded.current) return
      try {
        const res = await fetch(`${base}index.html?_=${Date.now()}`, { cache: 'no-store' })
        if (!res.ok) return
        const html = await res.text()
        const mm = html.match(/assets\/index-([A-Za-z0-9_-]+)\.js/)
        if (mm && mm[1] !== bootHash.current) {
          pending.current = true
          reloadIfHidden() // si ya está en segundo plano, recarga de inmediato
        }
      } catch {
        /* offline o fetch bloqueado: ignorar, se reintenta en el próximo tick */
      }
    }

    const onVisibility = () => {
      if (document.hidden) reloadIfHidden() // al dejar la pestaña, si hay pendiente → recarga
      else check() // al volver, re-chequea
    }

    const id = setInterval(check, intervalMs)
    document.addEventListener('visibilitychange', onVisibility)
    window.addEventListener('focus', check)
    check() // chequeo inicial

    return () => {
      clearInterval(id)
      document.removeEventListener('visibilitychange', onVisibility)
      window.removeEventListener('focus', check)
    }
  }, [intervalMs])
}
