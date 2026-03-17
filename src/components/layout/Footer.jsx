export default function Footer({ isOnline, pendingCount }) {
  return (
    <footer className="mt-auto">
      {/* Gold accent bar */}
      <div className="h-0.5 bg-gradient-to-r from-transparent via-igss-gold to-transparent" />

      <div className="bg-igss-900 text-white">
        <div className="max-w-3xl mx-auto px-4 py-3">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-1.5 text-[11px]">
            <div className="flex items-center gap-2">
              <div className={`w-1.5 h-1.5 rounded-full ${isOnline ? 'bg-igss-400' : 'bg-igss-red'} ${isOnline ? '' : 'animate-pulse'}`} />
              <span className="text-igss-300">
                {isOnline ? 'Conectado' : 'Sin conexión'}
                {pendingCount > 0 && (
                  <span className="text-igss-gold ml-1">
                    | {pendingCount} pendiente(s)
                  </span>
                )}
              </span>
            </div>
            <div className="text-igss-300/60 text-center">
              IGSS — Medicina Preventiva — Epidemiología
            </div>
            <div className="text-igss-300/40">
              &copy; {new Date().getFullYear()}
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
