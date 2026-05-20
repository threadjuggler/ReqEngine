/**
 * Scrollable box listing all links for a requirement.
 * Each row shows link type, the other side project_id+title as a clickable link,
 * and a delete button. Navigating to another requirement confirms if form is dirty.
 */

import { useNavigate } from 'react-router-dom';
import { deleteLink } from '../api/client';
import type { LinkItem } from '../api/types';
import { LINK_TYPE_LABELS } from '../api/types';
import { CreateLinkDialog } from './CreateLinkDialog';
import { useState } from 'react';

interface LinksBoxProps {
  /** The links to display; refreshed by the parent after mutations. */
  links: LinkItem[];
  /** Whether the parent form has unsaved changes (used for nav confirmation). */
  isDirty: boolean;
  /** Whether this is the unsaved new-requirement form (disables Create Link). */
  isNew: boolean;
  /** Called after a link is deleted or created so the parent refreshes data. */
  onLinksChanged: () => void;
}

/**
 * Renders the links table with delete buttons and a Create Link button.
 * Navigation to another requirement prompts if isDirty is true.
 * Create Link is disabled on the new-requirement form until first save.
 */
export function LinksBox({ links, isDirty, isNew, onLinksChanged }: LinksBoxProps) {
  const navigate = useNavigate();
  const [showDialog, setShowDialog] = useState(false);

  /** Navigate to the other side of a link, confirming if form is dirty. */
  function handleNavigate(otherId: number) {
    if (isDirty) {
      const confirmed = window.confirm(
        'You have unsaved changes. Discard them and navigate away?',
      );
      if (!confirmed) return;
    }
    void navigate(`/requirements/${otherId}`);
  }

  /** Delete a link by id and tell the parent to refresh. */
  async function handleDelete(linkId: number) {
    const confirmed = window.confirm('Delete this link?');
    if (!confirmed) return;
    try {
      await deleteLink(linkId);
      onLinksChanged();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete link.');
    }
  }

  return (
    <div className="links-section">
      <h3>Links</h3>

      <div className="links-box">
        {links.length === 0 ? (
          <p className="info-msg" style={{ padding: '10px 14px' }}>
            No links yet.
          </p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>Other Side</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {links.map((lnk) => (
                <tr key={lnk.link_id}>
                  <td>
                    {LINK_TYPE_LABELS[lnk.link_type as keyof typeof LINK_TYPE_LABELS] ??
                      lnk.link_type}
                  </td>
                  <td>
                    <button
                      className="link-href"
                      onClick={() => handleNavigate(lnk.other_side.id)}
                      title={`Navigate to ${lnk.other_side.project_id}`}
                    >
                      {lnk.other_side.project_id} — {lnk.other_side.title}
                    </button>
                  </td>
                  <td>
                    <button
                      className="btn-danger btn-sm"
                      onClick={() => void handleDelete(lnk.link_id)}
                    >
                      −
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="links-footer">
        <button
          className="btn-secondary"
          onClick={() => setShowDialog(true)}
          disabled={isNew}
          title={isNew ? 'Save the requirement first before adding links.' : undefined}
        >
          Create Link
        </button>
        {isNew && (
          <span className="disabled-note">
            Save the requirement first to enable link creation.
          </span>
        )}
      </div>

      {showDialog && (
        <CreateLinkDialog
          onCreated={() => {
            setShowDialog(false);
            onLinksChanged();
          }}
          onDiscard={() => setShowDialog(false)}
        />
      )}
    </div>
  );
}
