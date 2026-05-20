/**
 * React component rendered inside a TipTap RequirementRef node view.
 * Shows project name, title input, description textarea, type badge, and an "Open" link.
 * Loads the requirement on mount; title/description are debounced PUT on change.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRequirement, updateRequirement } from '../api/client';
import type { RequirementStatus, RequirementType } from '../api/types';
import { TYPE_LABELS } from '../api/types';

interface RequirementBoxProps {
  requirementId: number;
  projectId: string;
  requirementType: string;
  projectName: string;
  /** Called to check if the document has unsaved edits (for confirm dialog). */
  isDirty: boolean;
}

/**
 * Inline requirement box rendered as an atomic TipTap node.
 * Loads requirement data on mount and debounces PUT calls on input changes.
 * "Open" link navigates to /requirements/:id with a dirty-check confirm.
 */
export function RequirementBox({
  requirementId,
  requirementType,
  projectName,
  isDirty,
}: RequirementBoxProps) {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<RequirementStatus>('draft');
  const [reqType, setReqType] = useState<RequirementType | string>(requirementType);
  const [revision, setRevision] = useState('0.1');
  const [loading, setLoading] = useState(true);
  const [saveError, setSaveError] = useState<string | null>(null);

  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  /** Load the requirement data from the API on mount. */
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getRequirement(requirementId)
      .then((detail) => {
        if (cancelled) return;
        setTitle(detail.title);
        setDescription(detail.description);
        setStatus(detail.status as RequirementStatus);
        setReqType(detail.requirement_type);
        setRevision(detail.revision);
      })
      .catch(() => {
        // Silently ignore load failure — the node ref may be ahead of a save
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [requirementId]);

  /** Debounced PUT call triggered on every title/description change. */
  const scheduleSave = useCallback(
    (newTitle: string, newDesc: string) => {
      if (debounceTimer.current !== null) clearTimeout(debounceTimer.current);
      debounceTimer.current = setTimeout(() => {
        setSaveError(null);
        updateRequirement(requirementId, {
          title: newTitle,
          description: newDesc,
          status: status as RequirementStatus,
          requirement_type: reqType as RequirementType,
          revision,
        }).catch((err: unknown) => {
          setSaveError(err instanceof Error ? err.message : 'Save failed');
        });
      }, 500);
    },
    [requirementId, status, reqType, revision],
  );

  function handleTitleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const val = e.target.value;
    setTitle(val);
    scheduleSave(val, description);
  }

  function handleDescChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    const val = e.target.value;
    setDescription(val);
    scheduleSave(title, val);
  }

  function handleOpen() {
    if (isDirty) {
      const confirmed = window.confirm(
        'You have unsaved document changes. Discard them and navigate to the requirement?',
      );
      if (!confirmed) return;
    }
    void navigate(`/requirements/${requirementId}`);
  }

  const typeLabel =
    TYPE_LABELS[reqType as keyof typeof TYPE_LABELS] ?? reqType;

  return (
    <div className="requirement-box" contentEditable={false}>
      <div className="requirement-box-header">
        <span className="requirement-box-project">{projectName}</span>
        <span className="requirement-type-badge">{typeLabel}</span>
        <button
          className="requirement-open-link"
          onClick={handleOpen}
          title={`Open requirement ${requirementId}`}
        >
          Open →
        </button>
      </div>

      {loading ? (
        <p style={{ fontSize: 12, color: '#888' }}>Loading…</p>
      ) : (
        <>
          {saveError && (
            <p style={{ fontSize: 11, color: '#dc2626', margin: '4px 0' }}>{saveError}</p>
          )}
          <div className="requirement-box-field">
            <label className="requirement-box-label">Title:</label>
            <input
              type="text"
              maxLength={200}
              value={title}
              onChange={handleTitleChange}
              className="requirement-box-input"
            />
          </div>
          <div className="requirement-box-field">
            <label className="requirement-box-label">Description:</label>
            <textarea
              maxLength={500}
              value={description}
              onChange={handleDescChange}
              className="requirement-box-textarea"
              rows={3}
            />
          </div>
        </>
      )}
    </div>
  );
}
