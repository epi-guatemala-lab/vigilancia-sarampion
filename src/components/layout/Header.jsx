import { formTitle, formSubtitle, institutionName } from '../../config/formSchema.js'

export default function Header() {
  return (
    <header className="bg-gradient-to-r from-igss-dark via-igss-primary to-igss-secondary text-white shadow-lg">
      <div className="max-w-3xl mx-auto px-4 py-4">
        <div className="flex items-center gap-4">
          {/* IGSS Logo */}
          <div className="flex-shrink-0">
            <img
              src={`${import.meta.env.BASE_URL}igss-logo.png`}
              alt="Logo IGSS"
              className="w-16 h-16 sm:w-20 sm:h-20 object-contain drop-shadow-lg"
            />
          </div>

          <div className="flex-1 min-w-0">
            <p className="text-xs sm:text-sm text-green-200 font-medium uppercase tracking-wider">
              {institutionName}
            </p>
            <h1 className="text-base sm:text-xl font-bold leading-tight mt-0.5">
              {formTitle}
            </h1>
            <p className="text-xs sm:text-sm text-green-200 mt-0.5">
              {formSubtitle}
            </p>
            <p className="text-[10px] sm:text-xs text-green-300 mt-0.5">
              Subgerencia de Prestaciones en Servicios de Salud
            </p>
          </div>
        </div>
      </div>

      {/* Decorative gold bar */}
      <div className="h-1 bg-gradient-to-r from-igss-gold via-yellow-600 to-igss-gold" />
    </header>
  )
}
