/**
 * Modal dialog for creating OR editing a link between two objects.
 * Same UI in both modes; Save posts (create) or puts (edit) and invokes onSaved.
 * If `editing` is provided, the dialog is in edit mode for that link id.
 */

import { useState } from 'react';
import { createLink, updateLink } from '../api/client';
import type { LinkType } from '../api/types';
import { LINK_TYPE_LABELS, LINK_TYPE_VALUES } from '../api/types';

/** Initial values used when the dialog opens in edit mode. */
export interface LinkDialogEditing {
  link_id: number;
  link_type: LinkType;
  start_project_id: string;
  destination_project_id: string;
}

interface CreateLinkDialogProps {
  /** Called after a link is successfully created or updated so the parent can refresh. */
  onCreated: () => void;
  /** Called when the user cancels the dialog. */
  onDiscard: () => void;
  /** If set, the dialog opens in edit mode with these prefilled values. */
  editing?: LinkDialogEditing;
}

/**
 * Renders a modal overlay with a form to create or edit a link.
 * Validates that both fields are filled and different before submitting.
 * Surfaces backend error messages inline.
 */
export function CreateLinkDialog({ onCreated, onDiscard, editing }: CreateLinkDialogProps) {
  const isEdit = editing !== undefined;
  const [linkType, setLinkType] = useState<LinkType>(editing?.link_type ?? 'refines');
  const [startId, setStartId] = useState(editing?.start_project_id ?? '');
  const [destId, setDestId] = useState(editing?.destination_project_id ?? '');
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  /** Validates inputs and POSTs (create) or PUTs (edit) the link. */
  async function handleSave() {
    setError(null);
    if (!startId.trim() || !destId.trim()) {
      setError('Both link_start and link_destination are required.');
      return;
    }
    if (startId.trim() === destId.trim()) {
      setError('link_start and link_destination must be different.');
      return;
    }
    setSaving(true);
    try {
      const body = {
        link_type: linkType,
        link_start_project_id: startId.trim(),
        link_destination_project_id: destId.trim(),
      };
      if (isEdit && editing) {
        await updateLink(editing.link_id, body);
      } else {
        await createLink(body);
      }
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save link.');
    } finally {
      setSaving(false);
    }
  }

  const heading = isEdit ? 'Edit Link' : 'Create Link';

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-label={heading}>
      <div className="modal-card">
        <h2>{heading}</h2>

        <div className="form-group">
          <label htmlFor="dlg-link-type">Link Type</label>
          <select
            id="dlg-link-type"
            value={linkType}
            onChange={(e) => setLinkType(e.target.value as LinkType)}
          >
            {LINK_TYPE_VALUES.map((v) => (
              <option key={v} value={v}>
                {LINK_TYPE_LABELS[v]}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="dlg-link-start">Link Start</label>
          <input
            id="dlg-link-start"
            type="text"
            placeholder="Project1_00000007"
            value={startId}
            onChange={(e) => setStartId(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="dlg-link-dest">Link Destination</label>
          <input
            id="dlg-link-dest"
            type="text"
            placeholder="Project1_00000007"
            value={destId}
            onChange={(e) => setDestId(e.target.value)}
          />
        </div>

        {error && <p className="error-msg">{error}</p>}

        <div className="modal-actions">
          <button className="btn-secondary" onClick={onDiscard} disabled={saving}>
            Discard
          </button>
          <button className="btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
}
