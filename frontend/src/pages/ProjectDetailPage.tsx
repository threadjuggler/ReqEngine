/**
 * Project detail page at route "/projects/:projectId".
 * Shows project info, a documents table, and a link to requirements.
 * "Create New Document" button creates a blank doc and navigates to it.
 */

import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { createDocument, getProject, listProjectDocuments } from '../api/client';
import type { DocumentSummary, ProjectDetail } from '../api/types';

/**
 * Renders the project detail view with documents list.
 * Clicking a document row navigates to /documents/:id.
 * "Create New Document" POSTs to /api/documents then navigates.
 */
export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const projectIdNum = parseInt(projectId ?? '0', 10);

  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  /** Load project detail and documents on mount. */
  useEffect(() => {
    void loadData();
  }, [projectId]);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const [proj, docs] = await Promise.all([
        getProject(projectIdNum),
        listProjectDocuments(projectIdNum),
      ]);
      setProject(proj);
      setDocuments(docs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load project.');
    } finally {
      setLoading(false);
    }
  }

  /** Create a blank document and navigate to the editor. */
  async function handleCreateDocument() {
    setCreating(true);
    try {
      const doc = await createDocument(projectIdNum);
      void navigate(`/documents/${doc.id}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to create document.');
      setCreating(false);
    }
  }

  /** Format an ISO timestamp to a readable local string. */
  function formatDate(iso: string): string {
    return new Date(iso).toLocaleString();
  }

  if (loading) {
    return (
      <div className="page">
        <p className="info-msg">Loading…</p>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="page">
        <div className="page-error">{error ?? 'Project not found.'}</div>
        <button className="btn-secondary" onClick={() => void navigate('/')}>
          ← Back to Projects
        </button>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title">{project.project_name}</h1>
          <p className="info-msg" style={{ marginTop: 4 }}>
            ID: {project.id} &nbsp;|&nbsp; {project.document_count} document(s)
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <Link
            to={`/projects/${project.id}/requirements`}
            className="btn-secondary"
            style={{ textDecoration: 'none', padding: '6px 14px', borderRadius: 4 }}
          >
            View Requirements
          </Link>
          <button
            className="btn-primary"
            onClick={() => void handleCreateDocument()}
            disabled={creating}
          >
            {creating ? 'Creating…' : 'Create New Document'}
          </button>
        </div>
      </div>

      <button
        className="btn-secondary"
        style={{ marginBottom: 16 }}
        onClick={() => void navigate('/')}
      >
        ← Back to Projects
      </button>

      <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 12 }}>Documents</h2>

      {documents.length === 0 ? (
        <p className="info-msg">No documents yet. Create the first one.</p>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Project ID</th>
                <th>Author</th>
                <th>Last Edited</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr
                  key={doc.id}
                  className="clickable-row"
                  onClick={() => void navigate(`/documents/${doc.id}`)}
                >
                  <td>{doc.id}</td>
                  <td style={{ fontFamily: 'monospace' }}>{doc.project_id}</td>
                  <td>{doc.author}</td>
                  <td>{formatDate(doc.last_edit_on)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
