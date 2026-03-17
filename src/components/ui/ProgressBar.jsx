export default function ProgressBar({ currentStep, totalSteps, pageLabels, visiblePages }) {
  const progress = ((currentStep) / totalSteps) * 100
  const currentPageNum = visiblePages[currentStep - 1]
  const currentLabel = pageLabels[currentPageNum] || `Paso ${currentStep}`

  return (
    <div className="mb-6">
      {/* Step indicator */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-semibold text-igss-primary">
          Paso {currentStep} de {totalSteps}
        </span>
        <span className="text-sm text-gray-500 font-medium">
          {currentLabel}
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-igss-primary to-igss-accent rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Step dots */}
      <div className="flex justify-between mt-3">
        {visiblePages.map((pageNum, idx) => {
          const stepNum = idx + 1
          const isCompleted = stepNum < currentStep
          const isCurrent = stepNum === currentStep

          return (
            <div key={pageNum} className="flex flex-col items-center">
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 ${
                  isCompleted
                    ? 'bg-igss-green text-white'
                    : isCurrent
                      ? 'bg-igss-primary text-white ring-4 ring-igss-light'
                      : 'bg-gray-200 text-gray-500'
                }`}
              >
                {isCompleted ? (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  stepNum
                )}
              </div>
              <span className={`text-[10px] mt-1 text-center max-w-[60px] leading-tight hidden sm:block ${
                isCurrent ? 'text-igss-primary font-semibold' : 'text-gray-400'
              }`}>
                {pageLabels[pageNum]?.split(' ').slice(0, 2).join(' ')}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
