/**
 * Hook to track whether a form has unsaved changes (isDirty).
 * Registers a beforeunload handler while dirty to warn on browser refresh/close.
 * Returns isDirty flag, markDirty setter, and a reset function.
 */

import { useCallback, useEffect, useState } from 'react';

/** Tracks unsaved changes and warns on browser close/refresh if dirty. */
export function useDirtyForm() {
  const [isDirty, setIsDirty] = useState(false);

  /** Mark the form as having unsaved changes. */
  const markDirty = useCallback(() => setIsDirty(true), []);

  /** Reset the dirty state (call after save or intentional discard). */
  const resetDirty = useCallback(() => setIsDirty(false), []);

  useEffect(() => {
    if (!isDirty) return;

    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      e.preventDefault();
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isDirty]);

  return { isDirty, markDirty, resetDirty };
}
