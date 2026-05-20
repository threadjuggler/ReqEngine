/**
 * Edit/create form for a requirement.
 * Handles both /requirements/new (calls reserve-id on mount, then POST on save)
 * and /requirements/:id (loads full detail, then PUT on save).
 * Tracks dirty state and shows confirm dialogs for navigation-away when dirty.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  createRequirement,
  getRequirement,
  reserveId,
  updateRequirement,
} from '../api/client';
import type { LinkItem, RequirementDetail, RequirementStatus, RequirementType } from '../api/types';
import {
  STATUS_LABELS,
  STATUS_VALUES,
  TYPE_LABELS,
  TYPE_VALUES,
} from '../api/types';
import { LinksBox } from '../components/LinksBox';
import { useDirtyForm } from '../hooks/useDirtyForm';

/** Internal form state shape used for controlled inputs. */
interface FormState {
  title: string;
  description: string;
  status: RequirementStatus;
  requirement_type: RequirementType | '';
  revision: string;
}

/** Empty/default form values for a new requirement. */
const EMPTY_FORM: FormState = {
  title: '',
  description: '',
  status: 'draft',
  requirement_type: '',
  revision: '0.1',
};

/**
 * Renders the requirement create/edit form.
 * On new: reserves an ID on mount; on existing: loads detail from API.
 * Save, Clear Form, and Discard buttons all respect dirty-state confirmation.
 */
export function RequirementEdit() {
  const { id } = useParams<{ id: string }>();
  const isNew = id === undefined;
  const navigate = useNavigate();
  const { isDirty, markDirty, resetDirty } = useDirtyForm();

  // Reserved ID for the new form (stable across Clear Form)
  const [reservedProjectId, setReservedProjectId] = useState<string | null>(null);
  const [reservedNumber, setReservedNumber] = useState<number | null>(null);

  // Saved requirement detail (null = new unsaved form)
  const [savedDetail, setSavedDetail] = useState<RequirementDetail | null>(null);

  // Links list — kept separate so we can refresh it without re-fetching the whole form
  const [links, setLinks] = useState<LinkItem[]>([]);

  const [form, setForm] = useState<FormState>(EMPTY_FORM);

  // "Last saved" snapshot used by Clear Form on the edit route
  const lastSavedForm = useRef<FormState>(EMPTY_FORM);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);

  // Whether the requirement has been saved at least once in this session
  // (on /new it starts false; becomes true after first POST succeeds)
  const [savedOnce, setSavedOnce] = useState(!isNew);

  /** Convert a RequirementDetail into FormState for controlled inputs. */
  function detailToForm(d: RequirementDetail): FormState {
    return {
      title: d.title,
      description: d.description,
      status: d.status as RequirementStatus,
      requirement_type: d.requirement_type as RequirementType,
      revision: d.revision,
    };
  }

  // Guards against React 18 StrictMode double-invocation of the mount effect:
  // reserveId() is a non-idempotent server-side counter increment, so we must
  // call initialize() exactly once per route key.
  const didInitFor = useRef<string | null>(null);

  /** Load data on mount — reserve ID for /new, or fetch detail for /:id. */
  useEffect(() => {
    const key = id ?? 'new';
    if (didInitFor.current === key) return;
    didInitFor.current = key;
    void initialize();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function initialize() {
    setLoading(true);
    setPageError(null);
    try {
      if (isNew) {
        const reserved = await reserveId();
        setReservedProjectId(reserved.project_id);
        setReservedNumber(reserved.requirement_number);
        setForm(EMPTY_FORM);
        lastSavedForm.current = EMPTY_FORM;
        setSavedOnce(false);
        setLinks([]);
      } else {
        const numId = parseInt(id, 10);
        const detail = await getRequirement(numId);
        setSavedDetail(detail);
        const fs = detailToForm(detail);
        setForm(fs);
        lastSavedForm.current = fs;
        setLinks(detail.list_of_links);
        setSavedOnce(true);
      }
    } catch (err) {
      setPageError(err instanceof Error ? err.message : 'Failed to load.');
    } finally {
      setLoading(false);
    }
  }

  /** Generic controlled input change handler that also marks the form dirty. */
  function handleChange(
    field: keyof FormState,
    value: string,
  ) {
    setForm((prev) => ({ ...prev, [field]: value }));
    markDirty();
  }

  /** Save the form — POST for /new, PUT for /:id. */
  async function handleSave() {
    if (form.requirement_type === '') {
      alert('Please select a requirement type.');
      return;
    }
    setSaving(true);
    setPageError(null);
    try {
      let detail: RequirementDetail;
      if (isNew) {
        if (reservedProjectId === null || reservedNumber === null) {
          throw new Error('No reserved ID available.');
        }
        detail = await createRequirement({
          requirement_number: reservedNumber,
          project_id: reservedProjectId,
          title: form.title,
          description: form.description,
          status: form.status,
          requirement_type: form.requirement_type as RequirementType,
          revision: form.revision,
        });
      } else {
        detail = await updateRequirement(parseInt(id, 10), {
          title: form.title,
          description: form.description,
          status: form.status,
          requirement_type: form.requirement_type as RequirementType,
          revision: form.revision,
        });
      }
      setSavedDetail(detail);
      const fs = detailToForm(detail);
      setForm(fs);
      lastSavedForm.current = fs;
      setLinks(detail.list_of_links);
      setSavedOnce(true);
      resetDirty();
      if (isNew) {
        // Navigate to the edit route of the newly created requirement
        void navigate(`/requirements/${detail.id}`, { replace: true });
      }
    } catch (err) {
      setPageError(err instanceof Error ? err.message : 'Failed to save.');
    } finally {
      setSaving(false);
    }
  }

  /** Clear Form: restore to last saved values (or empty defaults for /new). */
  function handleClear() {
    setForm(lastSavedForm.current);
    resetDirty();
  }

  /** Discard: navigate back to list, confirming if dirty. */
  function handleDiscard() {
    if (isDirty) {
      const confirmed = window.confirm('You have unsaved changes. Discard them?');
      if (!confirmed) return;
    }
    resetDirty();
    void navigate('/');
  }

  /** Refresh the links list after a link is created or deleted. */
  const handleLinksChanged = useCallback(async () => {
    if (savedDetail === null) return;
    try {
      const detail = await getRequirement(savedDetail.id);
      setLinks(detail.list_of_links);
    } catch {
      // silently ignore; the user can refresh
    }
  }, [savedDetail]);

  /** The project_id shown as a non-editable label in the form. */
  const displayProjectId = isNew
    ? (reservedProjectId ?? '…')
    : (savedDetail?.project_id ?? '…');

  if (loading) {
    return (
      <div className="page">
        <p className="info-msg">Loading…</p>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">
          {isNew ? 'New Requirement' : `Edit ${displayProjectId}`}
        </h1>
        <button className="btn-secondary" onClick={handleDiscard}>
          ← Back to list
        </button>
      </div>

      {pageError && <div className="page-error">{pageError}</div>}

      <div className="form-card">
        {/* Project ID — read-only label */}
        <div className="form-group">
          <label>Project ID</label>
          <span className="field-label-value">{displayProjectId}</span>
        </div>

        <div className="form-group">
          <label htmlFor="req-title">Title</label>
          <input
            id="req-title"
            type="text"
            maxLength={200}
            value={form.title}
            onChange={(e) => handleChange('title', e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="req-desc">Description</label>
          <textarea
            id="req-desc"
            maxLength={500}
            value={form.description}
            onChange={(e) => handleChange('description', e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="req-status">Status</label>
          <select
            id="req-status"
            value={form.status}
            onChange={(e) => handleChange('status', e.target.value)}
          >
            {STATUS_VALUES.map((v) => (
              <option key={v} value={v}>
                {STATUS_LABELS[v]}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="req-type">
            Requirement Type <span style={{ color: 'var(--color-danger)' }}>*</span>
          </label>
          <select
            id="req-type"
            value={form.requirement_type}
            onChange={(e) => handleChange('requirement_type', e.target.value)}
          >
            <option value="" disabled>
              — select type —
            </option>
            {TYPE_VALUES.map((v) => (
              <option key={v} value={v}>
                {TYPE_LABELS[v]}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="req-revision">Revision</label>
          <input
            id="req-revision"
            type="text"
            maxLength={30}
            value={form.revision}
            onChange={(e) => handleChange('revision', e.target.value)}
          />
        </div>

        {/* Metadata — only shown for existing requirements */}
        {savedDetail !== null && (
          <dl className="form-meta">
            <dt>Author</dt>
            <dd>{savedDetail.author}</dd>
            <dt>Last edited by</dt>
            <dd>{savedDetail.last_edited_by}</dd>
            <dt>Created on</dt>
            <dd>{new Date(savedDetail.created_on).toLocaleString()}</dd>
            <dt>Last edited on</dt>
            <dd>{new Date(savedDetail.last_edited_on).toLocaleString()}</dd>
          </dl>
        )}

        <div className="form-actions">
          <button className="btn-primary" onClick={() => void handleSave()} disabled={saving}>
            {saving ? 'Saving…' : 'Save'}
          </button>
          <button className="btn-secondary" onClick={handleClear} disabled={saving}>
            Clear Form
          </button>
          <button className="btn-secondary" onClick={handleDiscard} disabled={saving}>
            Discard
          </button>
        </div>
      </div>

      {/* Links section */}
      <LinksBox
        links={links}
        isDirty={isDirty}
        isNew={isNew && !savedOnce}
        onLinksChanged={() => void handleLinksChanged()}
      />
    </div>
  );
}
