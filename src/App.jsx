import { useEffect, useState, useCallback } from 'react'
import Header from './components/layout/Header.jsx'
import Footer from './components/layout/Footer.jsx'
import FormWizard from './components/FormWizard.jsx'
import { retryPendingSubmissions, getPendingSubmissions } from './utils/sheetsApi.js'

const RETRY_INTERVAL_MS = 60_000  // reintento periódico de pendientes
const PENDING_REFRESH_MS = 5_000  // refresco del contador en footer

export default function App() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [pendingCount, setPendingCount] = useState(() => getPendingSubmissions().length)

  const refreshPendingCount = useCallback(() => {
    setPendingCount(getPendingSubmissions().length)
  }, [])

  const triggerRetry = useCallback(async () => {
    if (!navigator.onLine) return
    if (getPendingSubmissions().length === 0) return
    try {
      await retryPendingSubmissions()
    } finally {
      refreshPendingCount()
    }
  }, [refreshPendingCount])

  useEffect(() => {
    const onOnline = () => {
      setIsOnline(true)
      triggerRetry()
    }
    const onOffline = () => setIsOnline(false)
    const onFocus = () => triggerRetry()
    const onStorage = (e) => {
      if (e.key === 'sarampion_pending') refreshPendingCount()
    }

    window.addEventListener('online', onOnline)
    window.addEventListener('offline', onOffline)
    window.addEventListener('focus', onFocus)
    window.addEventListener('storage', onStorage)

    triggerRetry()

    const retryTimer = setInterval(triggerRetry, RETRY_INTERVAL_MS)
    const countTimer = setInterval(refreshPendingCount, PENDING_REFRESH_MS)

    return () => {
      window.removeEventListener('online', onOnline)
      window.removeEventListener('offline', onOffline)
      window.removeEventListener('focus', onFocus)
      window.removeEventListener('storage', onStorage)
      clearInterval(retryTimer)
      clearInterval(countTimer)
    }
  }, [triggerRetry, refreshPendingCount])

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 w-full max-w-3xl mx-auto px-3 sm:px-4 py-5 sm:py-8">
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-igss border border-white/60 p-5 sm:p-8">
          <FormWizard />
        </div>
      </main>

      <Footer isOnline={isOnline} pendingCount={pendingCount} />
    </div>
  )
}
