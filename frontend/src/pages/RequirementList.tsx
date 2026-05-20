/**
 * List view at route "/".
 * Fetches all requirements and shows them in a table with per-row delete buttons.
 * Top-right "New Requirement" button navigates to /requirements/new.
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { deleteRequirement, listRequirements } from '../api/client';
import type { RequirementSummary } from '../api/types';
import { STATUS_LABELS, TYPE_LABELS } from '../api/types';

/**
 * Renders the full requirements list table.
 * Clicking a row navigates to the edit form for that requirement.
 * The delete button shows a confirm dialog before calling the API.
 */
export function RequirementList() {
  const navigate = useNavigate();
  const [requirements, setRequirements] = useState<RequirementSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /** Load all requirements from the API on mount. */
  useEffect(() => {
    void loadRequirements();
  }, []);

  async function loadRequirements() {
    setLoading(true);
    setError(null);
    try {
      const data = await listRequirements();
      setRequirements(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load requirements.');
    } finally {
      setLoading(false);
    }
  }

  /** Delete a requirement after user confirmation, then refresh the list. */
  async function handleDelete(e: React.MouseEvent, id: number, projectId: string) {
    e.stopPropagation();
    const confirmed = window.confirm(
      `Delete requirement ${projectId}? This also deletes all its links.`,
    );
    if (!confirmed) return;
    try {
      await deleteRequirement(id);
      setRequirements((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete requirement.');
    }
  }

  /** Format an ISO timestamp to a readable local date+time string. */
  function formatDate(iso: string): string {
    return new Date(iso).toLocaleString();
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Requirements</h1>
        <button className="btn-primary" onClick={() => void navigate('/requirements/new')}>
          New Requirement
        </button>
      </div>

      {error && <div className="page-error">{error}</div>}

      {loading ? (
        <p className="info-msg">Loading…</p>
      ) : requirements.length === 0 ? (
        <p className="info-msg">No requirements found. Create the first one.</p>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Project ID</th>
                <th>Title</th>
                <th>Status</th>
                <th>Type</th>
                <th>Last Edited</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {requirements.map((req) => (
                <tr
                  key={req.id}
                  className="clickable-row"
                  onClick={() => void navigate(`/requirements/${req.id}`)}
                >
                  <td style={{ fontFamily: 'monospace' }}>{req.project_id}</td>
                  <td>{req.title}</td>
                  <td>
                    {STATUS_LABELS[req.status as keyof typeof STATUS_LABELS] ?? req.status}
                  </td>
                  <td>
                    {TYPE_LABELS[req.requirement_type as keyof typeof TYPE_LABELS] ??
                      req.requirement_type}
                  </td>
                  <td>{formatDate(req.last_edited_on)}</td>
                  <td>
                    <button
                      className="btn-danger btn-sm"
                      onClick={(e) => void handleDelete(e, req.id, req.project_id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
