export default function ErrorAlert({ message, onDismiss }) {
  if (!message) return null

  return (
    <div className="mb-5 bg-red-50 border border-igss-red/20 rounded-xl p-4 flex items-start gap-3 slide-up shadow-sm">
      <div className="w-8 h-8 rounded-full bg-igss-red/10 flex items-center justify-center flex-shrink-0">
        <svg className="w-4 h-4 text-igss-red" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <p className="flex-1 text-sm text-igss-red-dark pt-1">{message}</p>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-gray-400 hover:text-igss-red transition-colors p-1"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  )
}
