/**
 * Modal dialog for creating a new link between two requirements.
 * Accepts human project_ids (e.g. Project1_00000007) for both sides.
 * Calls POST /api/links on Save and invokes onCreated; Discard closes without action.
 */

import { useState } from 'react';
import { createLink } from '../api/client';
import type { LinkType } from '../api/types';
import { LINK_TYPE_LABELS, LINK_TYPE_VALUES } from '../api/types';

interface CreateLinkDialogProps {
  /** Called after a link is successfully created so the parent can refresh. */
  onCreated: () => void;
  /** Called when the user cancels the dialog. */
  onDiscard: () => void;
}

/**
 * Renders a modal overlay with a form to create a link.
 * Validates that both fields are filled and different before posting.
 * Surfaces backend error messages inline.
 */
export function CreateLinkDialog({ onCreated, onDiscard }: CreateLinkDialogProps) {
  const [linkType, setLinkType] = useState<LinkType>('refines');
  const [startId, setStartId] = useState('');
  const [destId, setDestId] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  /** Validates inputs and posts the link to the backend. */
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
      await createLink({
        link_type: linkType,
        link_start_project_id: startId.trim(),
        link_destination_project_id: destId.trim(),
      });
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create link.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-label="Create Link">
      <div className="modal-card">
        <h2>Create Link</h2>

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
