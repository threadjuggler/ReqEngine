/**
 * Scrollable box listing all links for a requirement.
 * Each row shows link type, the other-side project_id+title, and edit/delete buttons.
 * Other-side hyperlink navigates; Edit opens the link dialog prefilled; − deletes.
 */

import { useNavigate } from 'react-router-dom';
import { deleteLink } from '../api/client';
import type { LinkItem, LinkType } from '../api/types';
import { LINK_TYPE_LABELS } from '../api/types';
import { CreateLinkDialog, type LinkDialogEditing } from './CreateLinkDialog';
import { useState } from 'react';

interface LinksBoxProps {
  /** The links to display; refreshed by the parent after mutations. */
  links: LinkItem[];
  /** Whether the parent form has unsaved changes (used for nav confirmation). */
  isDirty: boolean;
  /** Whether this is the unsaved new-requirement form (disables Create Link). */
  isNew: boolean;
  /** Called after a link is created, edited, or deleted so the parent refreshes. */
  onLinksChanged: () => void;
}

/**
 * Renders the links table with edit and delete buttons and a Create Link button.
 * Edit reuses the same dialog as Create, prefilled with the existing values.
 * Other-side hyperlink navigation prompts if isDirty is true.
 */
export function LinksBox({ links, isDirty, isNew, onLinksChanged }: LinksBoxProps) {
  const navigate = useNavigate();
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<LinkDialogEditing | null>(null);

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

  /** Open the link dialog in edit mode with the row's current values prefilled. */
  function handleEdit(lnk: LinkItem) {
    setEditing({
      link_id: lnk.link_id,
      link_type: lnk.link_type as LinkType,
      start_project_id: lnk.start_project_id,
      destination_project_id: lnk.destination_project_id,
    });
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
                    {lnk.other_side.kind === 'requirement' ? (
                      <button
                        className="link-href"
                        onClick={() => handleNavigate(lnk.other_side.id)}
                        title={`Navigate to ${lnk.other_side.project_id}`}
                      >
                        {lnk.other_side.project_id} — {lnk.other_side.title}
                      </button>
                    ) : (
                      <span
                        className="link-testcase"
                        title="Testcase (no editor in step 1)"
                      >
                        <span className="kind-badge">Testcase</span>{' '}
                        {lnk.other_side.project_id} — {lnk.other_side.title}
                      </span>
                    )}
                  </td>
                  <td className="links-row-actions">
                    <button
                      className="btn-secondary btn-sm"
                      onClick={() => handleEdit(lnk)}
                      title="Edit this link"
                    >
                      ✎
                    </button>
                    <button
                      className="btn-danger btn-sm"
                      onClick={() => void handleDelete(lnk.link_id)}
                      title="Delete this link"
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
          onClick={() => setShowCreate(true)}
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

      {showCreate && (
        <CreateLinkDialog
          onCreated={() => {
            setShowCreate(false);
            onLinksChanged();
          }}
          onDiscard={() => setShowCreate(false)}
        />
      )}

      {editing !== null && (
        <CreateLinkDialog
          editing={editing}
          onCreated={() => {
            setEditing(null);
            onLinksChanged();
          }}
          onDiscard={() => setEditing(null)}
        />
      )}
    </div>
  );
}
