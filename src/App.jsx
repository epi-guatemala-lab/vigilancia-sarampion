import { useEffect } from 'react'
import Header from './components/layout/Header.jsx'
import Footer from './components/layout/Footer.jsx'
import FormWizard from './components/FormWizard.jsx'
import { retryPendingSubmissions, getPendingSubmissions } from './utils/sheetsApi.js'

export default function App() {
  const isOnline = typeof navigator !== 'undefined' ? navigator.onLine : true
  const pendingCount = getPendingSubmissions().length

  // Retry pending submissions on load
  useEffect(() => {
    if (navigator.onLine && getPendingSubmissions().length > 0) {
      retryPendingSubmissions()
    }
  }, [])

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />

      <main className="flex-1 w-full max-w-3xl mx-auto px-4 py-6">
        <div className="bg-white rounded-xl shadow-md border border-gray-100 p-5 sm:p-8">
          <FormWizard />
        </div>
      </main>

      <Footer isOnline={isOnline} pendingCount={pendingCount} />
    </div>
  )
}
