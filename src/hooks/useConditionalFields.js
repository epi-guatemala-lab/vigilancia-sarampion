import { useMemo } from 'react'
import { isFieldVisible, isPageVisible, getVisiblePages } from '../config/conditionalLogic.js'
import { formFields, getFieldsByPage, getTotalPages, pageLabels } from '../config/formSchema.js'

/**
 * Hook para manejar la lógica condicional de campos y páginas
 */
export function useConditionalFields(formData) {
  // Campos visibles por página
  const visibleFieldsByPage = useMemo(() => {
    const result = {}
    const totalPages = getTotalPages()
    for (let page = 1; page <= totalPages; page++) {
      const pageFields = getFieldsByPage(page)
      result[page] = pageFields.filter(f => isFieldVisible(f, formData))
    }
    return result
  }, [formData])

  // Páginas visibles (excluir páginas sin campos visibles)
  const visiblePages = useMemo(() => {
    return getVisiblePages(visibleFieldsByPage, formData)
  }, [visibleFieldsByPage, formData])

  // Verificar si un campo específico es visible
  const checkFieldVisible = (field) => {
    return isFieldVisible(field, formData)
  }

  // Obtener el label de una página
  const getPageLabel = (pageNum) => {
    return pageLabels[pageNum] || `Paso ${pageNum}`
  }

  return {
    visibleFieldsByPage,
    visiblePages,
    checkFieldVisible,
    getPageLabel,
  }
}
