/**
 * Typed fetch wrapper for the ReqEngine backend API.
 * All methods throw an Error with a human-readable message on HTTP errors.
 * Base URL is read from VITE_API_BASE_URL (default: http://localhost:8000/api).
 */

import type {
  Document,
  DocumentContent,
  DocumentSummary,
  LinkCreateBody,
  LinkOut,
  ProjectDetail,
  ProjectListItem,
  ProjectOut,
  RequirementCreateBody,
  RequirementDetail,
  RequirementSummary,
  RequirementUpdateBody,
  ReserveIdOut,
} from './types';

const BASE_URL: string =
  (import.meta.env['VITE_API_BASE_URL'] as string | undefined) ??
  'http://localhost:8000/api';

/**
 * Performs a fetch request and parses the JSON response.
 * Throws an Error with the backend detail message on non-2xx responses.
 * Returns null for 204 No Content responses.
 */
async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (res.status === 204) {
    return null as unknown as T;
  }

  const data: unknown = await res.json();

  if (!res.ok) {
    // Extract detail message from FastAPI error format or fallback
    const detail =
      data &&
      typeof data === 'object' &&
      'detail' in data &&
      typeof (data as Record<string, unknown>)['detail'] === 'string'
        ? (data as Record<string, string>)['detail']
        : `HTTP ${res.status}`;
    throw new Error(detail);
  }

  return data as T;
}

/** Reserve a new project_id for a forthcoming requirement creation. */
export async function reserveId(projectName = 'Project1'): Promise<ReserveIdOut> {
  return request<ReserveIdOut>(
    `/requirements/reserve-id?project_name=${encodeURIComponent(projectName)}`,
    { method: 'POST' },
  );
}

/** Fetch the list of all requirements (summary projection), optionally filtered by project. */
export async function listRequirements(projectIdNumber?: number): Promise<RequirementSummary[]> {
  const qs = projectIdNumber !== undefined ? `?project_id_number=${projectIdNumber}` : '';
  return request<RequirementSummary[]>(`/requirements${qs}`);
}

/** Fetch full detail for a single requirement by its numeric database id. */
export async function getRequirement(id: number): Promise<RequirementDetail> {
  return request<RequirementDetail>(`/requirements/${id}`);
}

/** Create a new requirement using a pre-reserved requirement_number and project_id. */
export async function createRequirement(
  body: RequirementCreateBody,
): Promise<RequirementDetail> {
  return request<RequirementDetail>('/requirements', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/** Update mutable fields of an existing requirement by its numeric id. */
export async function updateRequirement(
  id: number,
  body: RequirementUpdateBody,
): Promise<RequirementDetail> {
  return request<RequirementDetail>(`/requirements/${id}`, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
}

/** Delete a requirement (and cascade-delete its links) by numeric id. */
export async function deleteRequirement(id: number): Promise<void> {
  return request<void>(`/requirements/${id}`, { method: 'DELETE' });
}

/** Create a link between two requirements identified by their human project_ids. */
export async function createLink(body: LinkCreateBody): Promise<LinkOut> {
  return request<LinkOut>('/links', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/** Update an existing link's type and endpoints (same body shape as create). */
export async function updateLink(linkId: number, body: LinkCreateBody): Promise<LinkOut> {
  return request<LinkOut>(`/links/${linkId}`, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
}

/** Delete a link by its numeric id. */
export async function deleteLink(linkId: number): Promise<void> {
  return request<void>(`/links/${linkId}`, { method: 'DELETE' });
}

// ---- Project API ----

/** Fetch the list of all projects with document_count. */
export async function listProjects(): Promise<ProjectListItem[]> {
  return request<ProjectListItem[]>('/projects');
}

/** Create a new project by name. */
export async function createProject(projectName: string): Promise<ProjectOut> {
  return request<ProjectOut>('/projects', {
    method: 'POST',
    body: JSON.stringify({ project_name: projectName }),
  });
}

/** Fetch full project detail including document_ids. */
export async function getProject(id: number): Promise<ProjectDetail> {
  return request<ProjectDetail>(`/projects/${id}`);
}

/** Fetch summary list of documents belonging to a project. */
export async function listProjectDocuments(projectId: number): Promise<DocumentSummary[]> {
  return request<DocumentSummary[]>(`/projects/${projectId}/documents`);
}

// ---- Document API ----

/** Create a blank document within a project. */
export async function createDocument(projectIdNumber: number): Promise<Document> {
  return request<Document>('/documents', {
    method: 'POST',
    body: JSON.stringify({ project_id_number: projectIdNumber }),
  });
}

/** Fetch a full document including document_content. */
export async function getDocument(id: number): Promise<Document> {
  return request<Document>(`/documents/${id}`);
}

/** Save updated document_content (PUT /api/documents/:id). */
export async function updateDocument(
  id: number,
  documentContent: DocumentContent,
): Promise<Document> {
  return request<Document>(`/documents/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ document_content: documentContent }),
  });
}

/** Delete a document by its numeric id. */
export async function deleteDocument(id: number): Promise<void> {
  return request<void>(`/documents/${id}`, { method: 'DELETE' });
}
