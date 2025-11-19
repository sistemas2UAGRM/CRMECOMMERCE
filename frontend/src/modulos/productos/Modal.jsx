// frontend/src/modulos/productos/Modal.jsx
import React, { useEffect, useRef } from "react";
import { X } from "lucide-react";

/**
 * Modal accesible, responsive y con animaciones suaves.
 *
 * Props:
 * - abierto (bool)
 * - titulo (string)
 * - onCerrar (func)
 * - children (node)
 * - footer (node) optional
 * - size: "sm"|"md"|"lg"|"full" (default "md")
 * - closeLabel: accessible label for close button
 *
 * Requiere TailwindCSS con soporte `dark:` para modo oscuro.
 */
export default function Modal({
  abierto,
  titulo = "",
  onCerrar = () => {},
  children,
  footer = null,
  size = "md",
  closeLabel = "Cerrar",
}) {
  const overlayRef = useRef(null);
  const dialogRef = useRef(null);
  const previouslyFocused = useRef(null);

  // map de tamaños
  const sizeMap = {
    sm: "max-w-xl",
    md: "max-w-2xl",
    lg: "max-w-4xl",
    full: "w-full max-w-full",
  };
  const panelSizeClass = sizeMap[size] ?? sizeMap.md;

  // focus trap helpers
  const getFocusable = () => {
    if (!dialogRef.current) return [];
    return Array.from(
      dialogRef.current.querySelectorAll(
        'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])'
      )
    ).filter((el) => !el.hasAttribute("disabled") && !el.getAttribute("aria-hidden"));
  };

  useEffect(() => {
    if (!abierto) return;

    previouslyFocused.current = document.activeElement;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    // Delay para permitir animación
    requestAnimationFrame(() => {
      const focusables = getFocusable();
      (focusables[0] || dialogRef.current)?.focus();
    });

    const onKey = (e) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onCerrar();
        return;
      }
      if (e.key === "Tab") {
        const focusables = getFocusable();
        if (!focusables.length) {
          e.preventDefault();
          return;
        }
        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prevOverflow;
      previouslyFocused.current?.focus?.();
    };
  }, [abierto, onCerrar]);

  if (!abierto) return null;

  const onOverlayMouseDown = (e) => {
    if (e.target === overlayRef.current) onCerrar();
  };

  return (
    <div
      ref={overlayRef}
      onMouseDown={onOverlayMouseDown}
      className="fixed inset-0 z-[9999] flex items-start sm:items-center justify-center p-4 sm:p-6
                 bg-black/40 dark:bg-black/60 backdrop-blur-sm transition-opacity duration-300 ease-out"
      aria-hidden={false}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        tabIndex={-1}
        onMouseDown={(e) => e.stopPropagation()}
        className={`w-full ${panelSizeClass} bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800
                    text-slate-900 dark:text-slate-100 rounded-2xl shadow-2xl transform transition-all duration-400
                    ease-[cubic-bezier(.2,.9,.2,1)] translate-y-2 sm:translate-y-0 opacity-0 scale-95 sm:scale-100
                    animate-modal-in`}
        style={{ outline: "none" }}
      >
        {/* Header */}
        <header className="flex items-start sm:items-center justify-between gap-4 p-4 sm:p-5 border-b border-slate-100 dark:border-slate-800">
          <div className="flex-1 min-w-0">
            <h2 id="modal-title" className="text-lg sm:text-xl font-semibold truncate">
              {titulo}
            </h2>
          </div>

          <button
            onClick={onCerrar}
            aria-label={closeLabel}
            className="inline-flex items-center justify-center p-2 rounded-md text-slate-600 dark:text-slate-300
                       hover:bg-slate-100 dark:hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-offset-2
                       focus:ring-indigo-500 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </header>

        {/* Body: scrollable, nunca excede viewport */}
        <section
          className="p-4 sm:p-6 overflow-y-auto"
          style={{ maxHeight: "calc(100vh - 160px)" }}
          aria-labelledby="modal-title"
        >
          {children}
        </section>

        {/* Footer (opcional) */}
        {footer && (
          <footer className="p-4 sm:p-5 border-t border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row items-stretch sm:items-center gap-3 sm:gap-4 justify-end bg-transparent">
            {footer}
          </footer>
        )}

        {/* Animación fallback */}
        <style>{`
          @keyframes modalIn {
            0% { opacity: 0; transform: translateY(8px) scale(0.98); }
            60% { opacity: 1; transform: translateY(0) scale(1.01); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
          }
          .animate-modal-in { animation: modalIn 280ms cubic-bezier(.2,.9,.2,1) forwards; }
        `}</style>
      </div>
    </div>
  );
}
