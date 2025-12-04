import React from "react";

function PaginacionFusion({ currentPage, totalPages, totalItems, itemsPerPage, onPageChange }) {
  if (!totalPages || totalPages <= 1) return null;

  const goToPage = (p) => {
    if (p < 1 || p > totalPages || p === currentPage) return;
    onPageChange(p);
  };

  const renderPages = () => {
    const pages = [];
    const maxToShow = 5;
    let start = Math.max(1, currentPage - Math.floor(maxToShow / 2));
    let end = start + maxToShow - 1;
    if (end > totalPages) {
      end = totalPages;
      start = Math.max(1, end - maxToShow + 1);
    }
    if (start > 1) pages.push(
      <button key={1} className={`pf-page ${currentPage === 1 ? "active" : ""}`} onClick={() => goToPage(1)}>1</button>
    );
    if (start > 2) pages.push(<span key="start-ellipsis" className="pf-ellipsis">…</span>);
    for (let p = start; p <= end; p++) {
      pages.push(
        <button key={p} className={`pf-page ${currentPage === p ? "active" : ""}`} onClick={() => goToPage(p)}>{p}</button>
      );
    }
    if (end < totalPages - 1) pages.push(<span key="end-ellipsis" className="pf-ellipsis">…</span>);
    if (end < totalPages) pages.push(
      <button key={totalPages} className={`pf-page ${currentPage === totalPages ? "active" : ""}`} onClick={() => goToPage(totalPages)}>{totalPages}</button>
    );
    return pages;
  };

  return (
    <div style={{width: '100%', margin: '1.25rem 0 0.75rem'}}>
      <div className="pf-info" style={{textAlign: 'center', marginBottom: '1rem', fontSize: '.9rem'}}>
        {totalItems} resultados • Página {currentPage} de {totalPages}
      </div>
      <div style={{display: 'flex', justifyContent: 'center', gap: '0.5rem', flexWrap: 'wrap'}}>
        <button 
          className="pf-nav" 
          onClick={() => goToPage(currentPage - 1)} 
          disabled={currentPage === 1} 
          style={{
            padding: '.4rem .7rem', 
            borderRadius: '.4rem', 
            border: '1px solid var(--border-color, #e2e8f0)', 
            background: 'var(--bg-primary, #ffffff)',
            color: 'var(--text-primary, #1e293b)',
            cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
            opacity: currentPage === 1 ? 0.6 : 1,
            transition: 'all 0.2s ease'
          }}
        >
          Anterior
        </button>
        {renderPages()}
        <button 
          className="pf-nav" 
          onClick={() => goToPage(currentPage + 1)} 
          disabled={currentPage === totalPages} 
          style={{
            padding: '.4rem .7rem', 
            borderRadius: '.4rem', 
            border: '1px solid var(--border-color, #e2e8f0)', 
            background: 'var(--bg-primary, #ffffff)',
            color: 'var(--text-primary, #1e293b)',
            cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
            opacity: currentPage === totalPages ? 0.6 : 1,
            transition: 'all 0.2s ease'
          }}
        >
          Siguiente
        </button>
      </div>
      <style>
        {`
          .pf-info {
            color: var(--text-primary, #1e293b);
          }
          .pf-page { 
            padding: .4rem .7rem; 
            border-radius: .4rem; 
            border: 1px solid var(--border-color, #e2e8f0); 
            background: var(--bg-primary, #ffffff);
            color: var(--text-primary, #1e293b);
            cursor: pointer;
            transition: all 0.2s ease;
          }
          .pf-page:hover:not(.active) { 
            background: var(--bg-secondary, #f8fafc);
            border-color: var(--border-color, #e2e8f0);
          }
          .pf-page.active { 
            background: var(--color-red); 
            color: white !important; 
            border-color: var(--color-red); 
          }
          .pf-ellipsis { 
            padding: 0 .25rem; 
            color: var(--text-secondary, #64748b);
            display: flex;
            align-items: center;
          }
          
          /*dark mode estilos aligned with app*/
          [data-theme='dark'] .pf-info {
            color: #ffffff;
          }
          [data-theme='dark'] .pf-page {
            border-color: #334155;
            background: #1e293b;
            color: #e2e8f0;
          }
          [data-theme='dark'] .pf-page:hover:not(.active) {
            background: #334155;
            border-color: #334155;
          }
          [data-theme='dark'] .pf-ellipsis {
            color: #94a3b8;
          }
        `}
      </style>
    </div>
  );
}

export default PaginacionFusion;
