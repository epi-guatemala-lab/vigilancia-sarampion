import { useEffect, useState } from 'react'
import Header from './components/layout/Header.jsx'
import Footer from './components/layout/Footer.jsx'
import FormWizard from './components/FormWizard.jsx'
import { retryPendingSubmissions, getPendingSubmissions } from './utils/sheetsApi.js'

export default function App() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const pendingCount = getPendingSubmissions().length

  useEffect(() => {
    const onOnline = () => setIsOnline(true)
    const onOffline = () => setIsOnline(false)
    window.addEventListener('online', onOnline)
    window.addEventListener('offline', onOffline)

    if (navigator.onLine && getPendingSubmissions().length > 0) {
      retryPendingSubmissions()
    }

    return () => {
      window.removeEventListener('online', onOnline)
      window.removeEventListener('offline', onOffline)
    }
  }, [])

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
