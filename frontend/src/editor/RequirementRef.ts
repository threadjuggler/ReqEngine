/**
 * Custom TipTap block node extension for inline requirements.
 * Renders as an atomic block node using ReactNodeViewRenderer.
 * Attrs: requirement_id (int), project_id (str), requirement_type (str), project_name (str).
 */

import { Node } from '@tiptap/core';
import { ReactNodeViewRenderer } from '@tiptap/react';
import { RequirementRefNodeView } from './RequirementRefNodeView';

/**
 * Atomic block node that embeds a requirement reference into the document.
 * The node stores requirement_id + project metadata as attrs.
 * The rendered UI (RequirementBox) loads and edits the actual requirement via PUT.
 */
export const RequirementRef = Node.create({
  name: 'requirement-ref',

  group: 'block',

  atom: true,

  draggable: false,

  addAttributes() {
    return {
      requirement_id: {
        default: null,
        parseHTML: (el) => {
          const v = el.getAttribute('data-requirement-id');
          return v !== null ? parseInt(v, 10) : null;
        },
        renderHTML: (attrs) => ({
          'data-requirement-id': String(attrs['requirement_id'] as number),
        }),
      },
      project_id: {
        default: '',
        parseHTML: (el) => el.getAttribute('data-project-id') ?? '',
        renderHTML: (attrs) => ({ 'data-project-id': attrs['project_id'] as string }),
      },
      requirement_type: {
        default: 'customer_requirement',
        parseHTML: (el) => el.getAttribute('data-requirement-type') ?? 'customer_requirement',
        renderHTML: (attrs) => ({
          'data-requirement-type': attrs['requirement_type'] as string,
        }),
      },
      project_name: {
        default: '',
        parseHTML: (el) => el.getAttribute('data-project-name') ?? '',
        renderHTML: (attrs) => ({ 'data-project-name': attrs['project_name'] as string }),
      },
    };
  },

  parseHTML() {
    return [{ tag: 'div[data-requirement-id]' }];
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', HTMLAttributes];
  },

  addNodeView() {
    return ReactNodeViewRenderer(RequirementRefNodeView);
  },
});
