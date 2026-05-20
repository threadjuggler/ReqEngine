/**
 * Home page at route "/".
 * Shows all projects with document counts in a table.
 * "Create New Project" button opens a modal to enter a project name.
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createProject, listProjects } from '../api/client';
import type { ProjectListItem } from '../api/types';

/**
 * Renders the project list table and a "Create New Project" modal.
 * Clicking a row navigates to the project detail page.
 */
export function ProjectListPage() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<ProjectListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [newName, setNewName] = useState('');
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  /** Load all projects from the API on mount. */
  useEffect(() => {
    void loadProjects();
  }, []);

  async function loadProjects() {
    setLoading(true);
    setError(null);
    try {
      const data = await listProjects();
      setProjects(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects.');
    } finally {
      setLoading(false);
    }
  }

  /** Submit the modal form to create a new project. */
  async function handleCreate() {
    const trimmed = newName.trim();
    if (!trimmed) return;
    setCreating(true);
    setCreateError(null);
    try {
      const proj = await createProject(trimmed);
      setShowModal(false);
      setNewName('');
      void navigate(`/projects/${proj.id}`);
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : 'Failed to create project.');
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">Projects</h1>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          Create New Project
        </button>
      </div>

      {error && <div className="page-error">{error}</div>}

      {loading ? (
        <p className="info-msg">Loading…</p>
      ) : projects.length === 0 ? (
        <p className="info-msg">No projects found. Create the first one.</p>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Project Name</th>
                <th>Documents</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((p) => (
                <tr
                  key={p.id}
                  className="clickable-row"
                  onClick={() => void navigate(`/projects/${p.id}`)}
                >
                  <td>{p.id}</td>
                  <td>{p.project_name}</td>
                  <td>{p.document_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Project Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Project</h2>
            {createError && <div className="page-error">{createError}</div>}
            <div className="form-group">
              <label htmlFor="new-project-name">Project Name</label>
              <input
                id="new-project-name"
                type="text"
                maxLength={120}
                value={newName}
                autoFocus
                onChange={(e) => setNewName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') void handleCreate();
                  if (e.key === 'Escape') setShowModal(false);
                }}
              />
            </div>
            <div className="modal-actions">
              <button
                className="btn-secondary"
                onClick={() => {
                  setShowModal(false);
                  setNewName('');
                  setCreateError(null);
                }}
                disabled={creating}
              >
                Cancel
              </button>
              <button
                className="btn-primary"
                onClick={() => void handleCreate()}
                disabled={creating || !newName.trim()}
              >
                {creating ? 'Creating…' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
