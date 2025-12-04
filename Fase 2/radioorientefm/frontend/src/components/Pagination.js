import React from 'react';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import './Pagination.css';

/**
 * Componente de paginación reutilizable
 *
 * @param {number} currentPage - Página actual (1-indexed)
 * @param {number} totalPages - Total de páginas
 * @param {function} onPageChange - Callback cuando cambia la página
 * @param {number} pageSize - Tamaño de página actual
 * @param {function} onPageSizeChange - Callback cuando cambia el tamaño de página
 * @param {number} totalItems - Total de elementos
 * @param {boolean} showPageSize - Mostrar selector de tamaño de página
 */
const Pagination = ({
  currentPage,
  totalPages,
  onPageChange,
  pageSize = 20,
  onPageSizeChange,
  totalItems,
  showPageSize = true,
}) => {
  if (totalPages <= 1) return null;

  const pageSizeOptions = [10, 20, 50, 100];

  //generar array de números de página a mostrar
  const getPageNumbers = () => {
    const pages = [];
    const maxPagesToShow = 5;

    if (totalPages <= maxPagesToShow) {
      //mostrar todas las páginas si son pocas
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      //mostrar páginas con ellipsis
      const leftSiblingIndex = Math.max(currentPage - 1, 1);
      const rightSiblingIndex = Math.min(currentPage + 1, totalPages);

      const shouldShowLeftDots = leftSiblingIndex > 2;
      const shouldShowRightDots = rightSiblingIndex < totalPages - 1;

      if (!shouldShowLeftDots && shouldShowRightDots) {
        //mostrar: 1 2 3 4 5 ... 10
        for (let i = 1; i <= 5; i++) {
          pages.push(i);
        }
        pages.push('...');
        pages.push(totalPages);
      } else if (shouldShowLeftDots && !shouldShowRightDots) {
        //mostrar: 1 ... 6 7 8 9 10
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 4; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        //mostrar: 1 ... 4 5 6 ... 10
        pages.push(1);
        if (shouldShowLeftDots) pages.push('...');

        for (let i = leftSiblingIndex; i <= rightSiblingIndex; i++) {
          pages.push(i);
        }

        if (shouldShowRightDots) pages.push('...');
        pages.push(totalPages);
      }
    }

    return pages;
  };

  const pageNumbers = getPageNumbers();

  const handlePageSizeChange = (e) => {
    if (onPageSizeChange) {
      const newSize = parseInt(e.target.value, 10);
      onPageSizeChange(newSize);
      //volver a la primera página al cambiar el tamaño
      onPageChange(1);
    }
  };

  return (
    <div className="pagination-container">
      <div className="pagination-info">
        {totalItems && (
          <span className="pagination-text">
            Mostrando{' '}
            <strong>
              {Math.min((currentPage - 1) * pageSize + 1, totalItems)} -{' '}
              {Math.min(currentPage * pageSize, totalItems)}
            </strong>{' '}
            de <strong>{totalItems}</strong> resultados
          </span>
        )}
      </div>

      <div className="pagination-controls">
        {/*selector de tamaño de página*/}
        {showPageSize && onPageSizeChange && (
          <div className="page-size-selector">
            <label htmlFor="pageSize">Mostrar:</label>
            <select
              id="pageSize"
              value={pageSize}
              onChange={handlePageSizeChange}
              className="page-size-select"
            >
              {pageSizeOptions.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
            <span>por página</span>
          </div>
        )}

        {/*botones de paginación*/}
        <div className="pagination-buttons">
          {/*primera página*/}
          <button
            onClick={() => onPageChange(1)}
            disabled={currentPage === 1}
            className="pagination-btn"
            aria-label="Primera página"
          >
            <ChevronsLeft size={18} />
          </button>

          {/*página anterior*/}
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="pagination-btn"
            aria-label="Página anterior"
          >
            <ChevronLeft size={18} />
          </button>

          {/*números de página*/}
          {pageNumbers.map((page, index) => (
            page === '...' ? (
              <span key={`ellipsis-${index}`} className="pagination-ellipsis">
                ...
              </span>
            ) : (
              <button
                key={page}
                onClick={() => onPageChange(page)}
                className={`pagination-btn pagination-number ${
                  currentPage === page ? 'active' : ''
                }`}
                aria-label={`Página ${page}`}
                aria-current={currentPage === page ? 'page' : undefined}
              >
                {page}
              </button>
            )
          ))}

          {/*página siguiente*/}
          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="pagination-btn"
            aria-label="Página siguiente"
          >
            <ChevronRight size={18} />
          </button>

          {/*última página*/}
          <button
            onClick={() => onPageChange(totalPages)}
            disabled={currentPage === totalPages}
            className="pagination-btn"
            aria-label="Última página"
          >
            <ChevronsRight size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Pagination;
