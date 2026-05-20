/**
 * Project-scoped requirement list at route "/projects/:projectId/requirements".
 * Shows only requirements belonging to the project from the route param.
 * "New Requirement" navigates to /projects/:projectId/requirements/new.
 */

import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { deleteRequirement, getProject, listRequirements } from '../api/client';
import type { ProjectDetail, RequirementSummary } from '../api/types';
import { STATUS_LABELS, TYPE_LABELS } from '../api/types';

/**
 * Renders requirements filtered by the project id from the route.
 * Clicking a row navigates to /requirements/:id.
 * Delete button confirms then calls the API.
 */
export function RequirementListPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const projectIdNum = parseInt(projectId ?? '0', 10);

  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [requirements, setRequirements] = useState<RequirementSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /** Load project info and filtered requirements on mount. */
  useEffect(() => {
    void loadData();
  }, [projectId]);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const [proj, reqs] = await Promise.all([
        getProject(projectIdNum),
        listRequirements(projectIdNum),
      ]);
      setProject(proj);
      setRequirements(reqs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load requirements.');
    } finally {
      setLoading(false);
    }
  }

  /** Delete a requirement after confirmation and refresh the list. */
  async function handleDelete(e: React.MouseEvent, id: number, projectIdStr: string) {
    e.stopPropagation();
    const confirmed = window.confirm(
      `Delete requirement ${projectIdStr}? This also deletes all its links.`,
    );
    if (!confirmed) return;
    try {
      await deleteRequirement(id);
      setRequirements((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete requirement.');
    }
  }

  /** Format an ISO timestamp to a readable local string. */
  function formatDate(iso: string): string {
    return new Date(iso).toLocaleString();
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Requirements</h1>
          {project && (
            <p className="info-msg" style={{ marginTop: 4 }}>
              Project: {project.project_name}
            </p>
          )}
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button
            className="btn-secondary"
            onClick={() => void navigate(`/projects/${projectIdNum}`)}
          >
            ← Back to Project
          </button>
          <button
            className="btn-primary"
            onClick={() => void navigate(`/projects/${projectIdNum}/requirements/new`)}
          >
            New Requirement
          </button>
        </div>
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
