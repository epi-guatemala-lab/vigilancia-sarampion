import { formTitle, formSubtitle, institutionName } from '../../config/formSchema.js'

export default function Header() {
  return (
    <header className="bg-gradient-to-r from-igss-dark via-igss-primary to-igss-secondary text-white shadow-lg">
      <div className="max-w-3xl mx-auto px-4 py-4">
        <div className="flex items-center gap-4">
          {/* IGSS Logo */}
          <div className="flex-shrink-0">
            <div className="w-16 h-16 sm:w-20 sm:h-20 bg-white rounded-full flex items-center justify-center shadow-md">
              <svg viewBox="0 0 80 80" className="w-12 h-12 sm:w-16 sm:h-16">
                {/* Shield shape */}
                <defs>
                  <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#003876" />
                    <stop offset="100%" stopColor="#005DA8" />
                  </linearGradient>
                </defs>
                <path
                  d="M40 5 L70 15 L70 40 Q70 65 40 75 Q10 65 10 40 L10 15 Z"
                  fill="url(#shieldGrad)"
                  stroke="#C5960C"
                  strokeWidth="2"
                />
                {/* Cross */}
                <rect x="36" y="20" width="8" height="35" rx="2" fill="white" />
                <rect x="25" y="31" width="30" height="8" rx="2" fill="white" />
                {/* IGSS text */}
                <text
                  x="40"
                  y="68"
                  textAnchor="middle"
                  fontSize="8"
                  fontWeight="bold"
                  fill="#C5960C"
                  fontFamily="Arial, sans-serif"
                >
                  IGSS
                </text>
              </svg>
            </div>
          </div>

          <div className="flex-1 min-w-0">
            <p className="text-xs sm:text-sm text-blue-200 font-medium uppercase tracking-wider">
              {institutionName}
            </p>
            <h1 className="text-base sm:text-xl font-bold leading-tight mt-0.5">
              {formTitle}
            </h1>
            <p className="text-xs sm:text-sm text-blue-200 mt-0.5">
              {formSubtitle}
            </p>
            <p className="text-[10px] sm:text-xs text-blue-300 mt-0.5">
              Subgerencia de Prestaciones en Servicios de Salud
            </p>
          </div>
        </div>
      </div>

      {/* Decorative gold bar */}
      <div className="h-1 bg-gradient-to-r from-igss-gold via-yellow-500 to-igss-gold" />
    </header>
  )
}
