/**
 * Root application component.
 * Configures the React Router routes for the ReqEngine frontend.
 * Routes: "/" (list), "/requirements/new" (create), "/requirements/:id" (edit).
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import { RequirementList } from './pages/RequirementList';
import { RequirementEdit } from './pages/RequirementEdit';

/** Renders the top-level route structure. Unmatched paths redirect to "/". */
function App() {
  return (
    <Routes>
      <Route path="/" element={<RequirementList />} />
      <Route path="/requirements/new" element={<RequirementEdit />} />
      <Route path="/requirements/:id" element={<RequirementEdit />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
