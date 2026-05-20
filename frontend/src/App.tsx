/**
 * Root application component.
 * Configures the React Router routes for the ReqEngine frontend.
 * Routes: "/" (project list), "/projects/:id" (detail), "/documents/:id" (editor),
 * "/projects/:projectId/requirements" (requirement list), "/requirements/:id" (edit).
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import { ProjectListPage } from './pages/ProjectListPage';
import { ProjectDetailPage } from './pages/ProjectDetailPage';
import { RequirementListPage } from './pages/RequirementListPage';
import { RequirementEdit } from './pages/RequirementEdit';
import { DocumentEditorPage } from './pages/DocumentEditorPage';

/** Renders the top-level route structure. Unmatched paths redirect to "/". */
function App() {
  return (
    <Routes>
      {/* Home — project list */}
      <Route path="/" element={<ProjectListPage />} />

      {/* Project detail */}
      <Route path="/projects/:projectId" element={<ProjectDetailPage />} />

      {/* Create a new document (redirects to /documents/:id after creation) */}
      <Route
        path="/projects/:projectId/documents/new"
        element={<DocumentEditorPage />}
      />

      {/* Document editor */}
      <Route path="/documents/:documentId" element={<DocumentEditorPage />} />

      {/* Project-scoped requirement list */}
      <Route
        path="/projects/:projectId/requirements"
        element={<RequirementListPage />}
      />

      {/* New requirement scoped to a project */}
      <Route
        path="/projects/:projectId/requirements/new"
        element={<RequirementEdit />}
      />

      {/* Edit existing requirement */}
      <Route path="/requirements/:id" element={<RequirementEdit />} />

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
