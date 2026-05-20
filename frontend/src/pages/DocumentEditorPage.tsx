/**
 * Document editor page at /documents/:documentId or /projects/:projectId/documents/new.
 * In new mode: POSTs a blank document, then redirects to /documents/:newId.
 * In edit mode: GETs the document and hydrates the TipTap editor.
 * Toolbar: style dropdown, font, size, bold/italic/underline, add requirement, save.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { TextStyle, FontSize } from '@tiptap/extension-text-style';
import { FontFamily } from '@tiptap/extension-font-family';
import Underline from '@tiptap/extension-underline';

import { createDocument, createRequirement, getDocument, getProject, reserveId, updateDocument } from '../api/client';
import type { DocumentContent, RequirementStatus, RequirementType } from '../api/types';
import { TYPE_VALUES, TYPE_LABELS } from '../api/types';
import { HeadingExt } from '../editor/HeadingExt';
import { RequirementRef } from '../editor/RequirementRef';
import { ChapterNumbering } from '../editor/ChapterNumbering';
import { useDirtyForm } from '../hooks/useDirtyForm';

/** Font family options for the toolbar dropdown. */
const FONT_FAMILIES = [
  { label: 'Arial', value: 'Arial, sans-serif' },
  { label: 'Helvetica', value: 'Helvetica, sans-serif' },
  { label: 'Times New Roman', value: '"Times New Roman", serif' },
  { label: 'Courier New', value: '"Courier New", monospace' },
];

/** Font size options for the toolbar dropdown. */
const FONT_SIZES = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24];

/** Style options: Standard (paragraph) + Heading 1-8. */
const STYLE_OPTIONS = [
  { label: 'Standard', value: 'paragraph' },
  ...Array.from({ length: 8 }, (_, i) => ({
    label: `Heading ${i + 1}`,
    value: `heading-${i + 1}`,
  })),
];

/**
 * Main document editor page.
 * In "new" mode (route has projectId), creates a blank document on mount.
 * In "edit" mode (route has documentId), loads and hydrates the editor.
 */
export function DocumentEditorPage() {
  // Route params — one of projectId (new mode) or documentId (edit mode) will be set
  const { projectId, documentId } = useParams<{ projectId: string; documentId: string }>();
  const isNew = projectId !== undefined && documentId === undefined;
  const navigate = useNavigate();
  const { isDirty, markDirty, resetDirty } = useDirtyForm();

  const [docId, setDocId] = useState<number | null>(
    documentId !== undefined ? parseInt(documentId, 10) : null,
  );
  const [projectInfo, setProjectInfo] = useState<{ id: number; name: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Current style selection in the toolbar
  const [selectedStyle, setSelectedStyle] = useState('paragraph');
  const [selectedFont, setSelectedFont] = useState(FONT_FAMILIES[0]!.value);
  const [selectedSize, setSelectedSize] = useState(10);
  const [selectedReqType, setSelectedReqType] = useState<RequirementType>('customer_requirement');

  const didInit = useRef(false);

  // The custom Heading extension with StarterKit's built-in heading disabled
  const extensions = [
    StarterKit.configure({ heading: false }),
    HeadingExt,
    ChapterNumbering,
    TextStyle,
    FontSize,
    FontFamily,
    Underline,
    RequirementRef,
  ];

  const editor = useEditor({
    extensions,
    content: { type: 'doc', content: [{ type: 'paragraph' }] },
    onUpdate: () => {
      markDirty();
    },
    editorProps: {
      attributes: {
        class: 'document-editor-inner',
        'data-document-dirty': isDirty ? 'true' : 'false',
      },
    },
  });

  // Sync isDirty to the editor DOM element so RequirementRefNodeView can read it
  useEffect(() => {
    if (editor) {
      const el = editor.view.dom as HTMLElement;
      el.dataset['documentDirty'] = isDirty ? 'true' : 'false';
    }
  }, [isDirty, editor]);

  /** Initialize: create blank doc (new mode) or load existing doc (edit mode). */
  useEffect(() => {
    if (didInit.current) return;
    didInit.current = true;
    void initialize();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function initialize() {
    setLoading(true);
    setError(null);
    try {
      if (isNew && projectId !== undefined) {
        const projIdNum = parseInt(projectId, 10);
        const proj = await getProject(projIdNum);
        const doc = await createDocument(projIdNum);
        setProjectInfo({ id: proj.id, name: proj.project_name });
        setDocId(doc.id);
        // Redirect to the stable edit URL
        navigate(`/documents/${doc.id}`, { replace: true });
      } else if (documentId !== undefined) {
        const doc = await getDocument(parseInt(documentId, 10));
        setDocId(doc.id);
        // Load project info for the requirement-add button
        try {
          const proj = await getProject(doc.project_id_number);
          setProjectInfo({ id: proj.id, name: proj.project_name });
        } catch {
          // Non-fatal — project info is optional for the editor
        }
        // Hydrate the editor once it's ready
        if (editor && doc.document_content && Object.keys(doc.document_content).length > 0) {
          editor.commands.setContent(doc.document_content as DocumentContent);
        } else {
          // Store the content to set once the editor mounts
          pendingContent.current = doc.document_content as DocumentContent | null;
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load document.');
    } finally {
      setLoading(false);
      resetDirty();
    }
  }

  // Store content to set once the editor mounts (if editor wasn't ready during initialize)
  const pendingContent = useRef<DocumentContent | null>(null);

  // Set pending content once editor becomes available
  useEffect(() => {
    if (editor && pendingContent.current) {
      editor.commands.setContent(pendingContent.current);
      pendingContent.current = null;
      resetDirty();
    }
  }, [editor, resetDirty]);

  /** Save the document by PUTting the current editor JSON. */
  const handleSave = useCallback(async () => {
    if (!editor || docId === null) return;
    setSaving(true);
    setSaveError(null);
    try {
      const content = editor.getJSON() as DocumentContent;
      await updateDocument(docId, content);
      resetDirty();
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Failed to save.');
    } finally {
      setSaving(false);
    }
  }, [editor, docId, resetDirty]);

  /** Apply the selected style (paragraph or heading level) to the current line. */
  function handleStyleChange(value: string) {
    setSelectedStyle(value);
    if (!editor) return;
    if (value === 'paragraph') {
      editor.chain().focus().setParagraph().run();
    } else {
      const level = parseInt(value.replace('heading-', ''), 10);
      editor.chain().focus().setHeading({ level: level as 1 }).run();
    }
  }

  /** Apply font family to the current selection. */
  function handleFontChange(value: string) {
    setSelectedFont(value);
    if (!editor) return;
    editor.chain().focus().setFontFamily(value).run();
  }

  /** Apply font size to the current selection using the FontSize extension. */
  function handleSizeChange(size: number) {
    setSelectedSize(size);
    if (!editor) return;
    editor.chain().focus().setFontSize(`${size}pt`).run();
  }

  /** Add a requirement node at the current cursor position. */
  async function handleAddRequirement() {
    if (!editor || !projectInfo) {
      alert('Document must be saved and associated with a project first.');
      return;
    }
    try {
      // 1. Reserve an ID for this project
      const reserved = await reserveId(projectInfo.name);

      // 2. Create the requirement row
      const req = await createRequirement({
        requirement_number: reserved.requirement_number,
        project_id: reserved.project_id,
        project_id_number: projectInfo.id,
        title: '',
        description: '',
        status: 'draft' as RequirementStatus,
        requirement_type: selectedReqType,
        revision: '0.1',
      });

      // 3. Insert the requirement-ref node at the cursor
      editor
        .chain()
        .focus()
        .insertContent({
          type: 'requirement-ref',
          attrs: {
            requirement_id: req.id,
            project_id: req.project_id,
            requirement_type: selectedReqType,
            project_name: projectInfo.name,
          },
        })
        .run();

      markDirty();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to add requirement.');
    }
  }

  // Keep the toolbar style dropdown in sync with the editor's current node type
  useEffect(() => {
    if (!editor) return;
    const updateStyle = () => {
      if (editor.isActive('paragraph')) {
        setSelectedStyle('paragraph');
      } else {
        for (let i = 1; i <= 8; i++) {
          if (editor.isActive('heading', { level: i })) {
            setSelectedStyle(`heading-${i}`);
            break;
          }
        }
      }
    };
    editor.on('selectionUpdate', updateStyle);
    editor.on('transaction', updateStyle);
    return () => {
      editor.off('selectionUpdate', updateStyle);
      editor.off('transaction', updateStyle);
    };
  }, [editor]);

  if (loading) {
    return (
      <div className="page">
        <p className="info-msg">Loading document…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <div className="page-error">{error}</div>
        <button className="btn-secondary" onClick={() => void navigate('/')}>
          ← Back to Projects
        </button>
      </div>
    );
  }

  return (
    <div className="document-editor-page">
      {/* Fixed toolbar */}
      <div className="doc-toolbar">
        {/* Back navigation */}
        <button
          className="btn-secondary btn-sm"
          onClick={() => {
            if (isDirty) {
              const ok = window.confirm('You have unsaved changes. Discard and go back?');
              if (!ok) return;
            }
            if (projectInfo) {
              void navigate(`/projects/${projectInfo.id}`);
            } else {
              void navigate('/');
            }
          }}
        >
          ←
        </button>

        <div className="doc-toolbar-sep" />

        {/* Style dropdown */}
        <select
          value={selectedStyle}
          onChange={(e) => handleStyleChange(e.target.value)}
          title="Text style"
        >
          {STYLE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* Font family dropdown */}
        <select
          value={selectedFont}
          onChange={(e) => handleFontChange(e.target.value)}
          title="Font family"
        >
          {FONT_FAMILIES.map((f) => (
            <option key={f.value} value={f.value}>
              {f.label}
            </option>
          ))}
        </select>

        {/* Font size dropdown */}
        <select
          value={selectedSize}
          onChange={(e) => handleSizeChange(parseInt(e.target.value, 10))}
          title="Font size"
          style={{ width: 60 }}
        >
          {FONT_SIZES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>

        <div className="doc-toolbar-sep" />

        {/* Bold */}
        <button
          className={`doc-toolbar-btn${editor?.isActive('bold') ? ' active' : ''}`}
          onClick={() => editor?.chain().focus().toggleBold().run()}
          title="Bold"
        >
          <strong>B</strong>
        </button>

        {/* Italic */}
        <button
          className={`doc-toolbar-btn${editor?.isActive('italic') ? ' active' : ''}`}
          onClick={() => editor?.chain().focus().toggleItalic().run()}
          title="Italic"
        >
          <em>I</em>
        </button>

        {/* Underline */}
        <button
          className={`doc-toolbar-btn${editor?.isActive('underline') ? ' active' : ''}`}
          onClick={() => editor?.chain().focus().toggleUnderline().run()}
          title="Underline"
        >
          <span style={{ textDecoration: 'underline' }}>U</span>
        </button>

        <div className="doc-toolbar-sep" />

        {/* Add Requirement */}
        <select
          value={selectedReqType}
          onChange={(e) => setSelectedReqType(e.target.value as RequirementType)}
          title="Requirement type"
        >
          {TYPE_VALUES.map((t) => (
            <option key={t} value={t}>
              {TYPE_LABELS[t]}
            </option>
          ))}
        </select>
        <button
          className="btn-primary btn-sm"
          onClick={() => void handleAddRequirement()}
          disabled={!projectInfo}
          title={!projectInfo ? 'Project info not loaded yet' : 'Add requirement at cursor'}
        >
          + Add Requirement
        </button>

        <div className="doc-toolbar-spacer" />

        {/* Dirty indicator */}
        {isDirty && <span className="doc-dirty-indicator">Unsaved</span>}

        {/* Save */}
        {saveError && <span className="doc-save-error">{saveError}</span>}
        <button
          className="btn-primary btn-sm"
          onClick={() => void handleSave()}
          disabled={saving || !isDirty}
        >
          {saving ? 'Saving…' : 'Save'}
        </button>
      </div>

      {/* DIN A4 page surface */}
      <div className="document-page-wrapper">
        <div className="document-page">
          {editor && <EditorContent editor={editor} />}
        </div>
      </div>
    </div>
  );
}
