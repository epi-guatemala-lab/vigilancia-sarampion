export default function ProgressBar({ currentStep, totalSteps, pageLabels, visiblePages }) {
  const progress = ((currentStep) / totalSteps) * 100
  const currentPageNum = visiblePages[currentStep - 1]
  const currentLabel = pageLabels[currentPageNum] || `Paso ${currentStep}`

  return (
    <div className="mb-8">
      {/* Step indicator */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-igss-800 text-white text-xs font-bold">
            {currentStep}
          </span>
          <span className="text-sm font-bold text-igss-800">
            de {totalSteps}
          </span>
        </div>
        <span className="text-sm text-igss-700 font-semibold">
          {currentLabel}
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-igss-100 rounded-full h-2 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{
            width: `${progress}%`,
            background: 'linear-gradient(90deg, #1B5E20 0%, #2E7D32 50%, #43A047 100%)',
          }}
        />
      </div>

      {/* Step dots - compact */}
      <div className="flex justify-between mt-4 px-1">
        {visiblePages.map((pageNum, idx) => {
          const stepNum = idx + 1
          const isCompleted = stepNum < currentStep
          const isCurrent = stepNum === currentStep

          return (
            <div key={pageNum} className="flex flex-col items-center gap-1.5">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-500 ${
                  isCompleted
                    ? 'bg-igss-700 text-white shadow-sm'
                    : isCurrent
                      ? 'bg-igss-gold text-white shadow-md ring-[3px] ring-igss-gold/30'
                      : 'bg-gray-200 text-gray-400'
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
              <span className={`text-[9px] text-center max-w-[56px] leading-tight hidden sm:block ${
                isCurrent ? 'text-igss-800 font-bold' : isCompleted ? 'text-igss-600' : 'text-gray-400'
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
