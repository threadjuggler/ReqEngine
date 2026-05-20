/**
 * TipTap React node view wrapper for the requirement-ref node.
 * Bridges the TipTap NodeViewWrapper API with the RequirementBox React component.
 * Receives node attrs from TipTap and passes them to RequirementBox.
 */

import { NodeViewWrapper } from '@tiptap/react';
import type { ReactNodeViewProps } from '@tiptap/react';
import { RequirementBox } from './RequirementBox';

/** Renders the RequirementBox inside a TipTap NodeViewWrapper for the requirement-ref node. */
export function RequirementRefNodeView({ node, editor }: ReactNodeViewProps) {
  const attrs = node.attrs as {
    requirement_id: number;
    project_id: string;
    requirement_type: string;
    project_name: string;
  };

  // Pass isDirty via a custom data attribute on the editor's element
  // (the editor itself doesn't expose document dirty state, but the DocumentEditorPage
  // keeps track of it). We use a dataset approach to avoid prop drilling.
  const editorEl = editor.view.dom as HTMLElement;
  const isDirty = editorEl.dataset['documentDirty'] === 'true';

  return (
    <NodeViewWrapper>
      <RequirementBox
        requirementId={attrs.requirement_id}
        projectId={attrs.project_id}
        requirementType={attrs.requirement_type}
        projectName={attrs.project_name}
        isDirty={isDirty}
      />
    </NodeViewWrapper>
  );
}
