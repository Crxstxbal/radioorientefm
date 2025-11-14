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
    <div className="pf-wrapper" style={{display: "flex", alignItems: "center", justifyContent: "space-between", gap: "1rem", marginTop: "2rem", flexWrap: "wrap"}}>
      <div className="pf-info" style={{color: "var(--color-gray-600)", fontSize: ".9rem"}}>
        {totalItems} resultados • Página {currentPage} de {totalPages}
      </div>
      <div className="pf-controls" style={{display: "flex", alignItems: "center", gap: ".5rem", flexWrap: "wrap"}}>
        <button className="pf-nav" onClick={() => goToPage(currentPage - 1)} disabled={currentPage === 1} style={{padding: ".4rem .7rem", borderRadius: ".4rem", border: "1px solid var(--color-gray-200)", background: "white", cursor: currentPage === 1 ? "not-allowed" : "pointer"}}>Anterior</button>
        {renderPages()}
        <button className="pf-nav" onClick={() => goToPage(currentPage + 1)} disabled={currentPage === totalPages} style={{padding: ".4rem .7rem", borderRadius: ".4rem", border: "1px solid var(--color-gray-200)", background: "white", cursor: currentPage === totalPages ? "not-allowed" : "pointer"}}>Siguiente</button>
      </div>
      <style>
        {`
          .pf-page { padding: .4rem .7rem; border-radius: .4rem; border: 1px solid var(--color-gray-200); background: white; cursor: pointer; }
          .pf-page.active { background: var(--color-red); color: white; border-color: var(--color-red); }
          .pf-page:hover { border-color: var(--color-gray-300); }
          .pf-ellipsis { padding: 0 .25rem; color: var(--color-gray-500); }
        `}
      </style>
    </div>
  );
}

export default PaginacionFusion;
