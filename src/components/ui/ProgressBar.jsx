export default function ProgressBar({ currentStep, totalSteps, pageLabels, visiblePages, onStepClick }) {
  return (
    <div className="mb-8">
      {/* Step dots with connecting line */}
      <div className="relative flex justify-between items-start">
        {/* Background line */}
        <div className="absolute top-4 left-4 right-4 h-0.5 bg-gray-200" />
        {/* Progress line */}
        <div
          className="absolute top-4 left-4 h-0.5 transition-all duration-700 ease-out"
          style={{
            width: `calc(${((currentStep - 1) / (totalSteps - 1)) * 100}% - 32px + ${(currentStep - 1) / (totalSteps - 1) * 32}px)`,
            background: 'linear-gradient(90deg, #1B5E20, #2E7D32)',
          }}
        />

        {visiblePages.map((pageNum, idx) => {
          const stepNum = idx + 1
          const isCompleted = stepNum < currentStep
          const isCurrent = stepNum === currentStep
          const isClickable = typeof onStepClick === 'function' && stepNum < currentStep
          const label = pageLabels[pageNum] || ''

          const circleClasses = `w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-500 ${
            isCompleted
              ? `bg-igss-700 text-white shadow-sm ${isClickable ? 'hover:bg-igss-800 hover:shadow-md' : ''}`
              : isCurrent
                ? 'bg-igss-gold text-white shadow-md ring-[3px] ring-igss-gold/25'
                : 'bg-white text-gray-400 border-2 border-gray-200'
          }`

          const labelClasses = `text-[9px] mt-1.5 text-center leading-tight hidden sm:block max-w-[64px] ${
            isCurrent ? 'text-igss-800 font-bold' : isCompleted ? 'text-igss-600 font-medium' : 'text-gray-400'
          }`

          const inner = (
            <>
              <div className={circleClasses}>
                {isCompleted ? (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  stepNum
                )}
              </div>
              <span className={labelClasses}>
                {label.split(' ').slice(0, 2).join(' ')}
              </span>
            </>
          )

          return (
            <div key={pageNum} className="relative flex flex-col items-center z-10" style={{ width: `${100 / totalSteps}%` }}>
              {isClickable ? (
                <button
                  type="button"
                  onClick={() => onStepClick(stepNum)}
                  title={`Volver al Paso ${stepNum}: ${label}`}
                  aria-label={`Volver al Paso ${stepNum}: ${label}`}
                  className="flex flex-col items-center bg-transparent border-0 p-0 cursor-pointer focus:outline-none focus:ring-2 focus:ring-igss-gold/50 rounded-full"
                >
                  {inner}
                </button>
              ) : (
                <div className="flex flex-col items-center" aria-current={isCurrent ? 'step' : undefined}>
                  {inner}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Current step label - mobile */}
      <div className="flex items-center justify-between mt-4 sm:hidden">
        <span className="text-xs font-bold text-igss-800">
          Paso {currentStep}/{totalSteps}
        </span>
        <span className="text-xs font-semibold text-igss-gold-dark">
          {pageLabels[visiblePages[currentStep - 1]]}
        </span>
      </div>
    </div>
  )
}
