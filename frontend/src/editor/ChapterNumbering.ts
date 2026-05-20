/**
 * TipTap Extension that computes and renders chapter numbers as ProseMirror decorations.
 * Walks all heading nodes in document order on every transaction.
 * Numbers are computed at render time and NOT stored in the document JSON.
 */

import { Extension } from '@tiptap/core';
import { Plugin, PluginKey } from '@tiptap/pm/state';
import type { Node } from '@tiptap/pm/model';
import { Decoration, DecorationSet } from '@tiptap/pm/view';

/** Plugin key for the chapter-numbering plugin. */
const chapterNumberingKey = new PluginKey<DecorationSet>('chapterNumbering');

/**
 * Builds the chapter number prefix string for a heading at the given level.
 * Convention: if a level is skipped (e.g. heading-3 without preceding heading-2),
 * the intermediate counter stays at 0 and is included: e.g. "1.0.1".
 * This is predictable and deterministic even if unconventional.
 */
function buildChapterPrefix(counters: number[], level: number): string {
  return counters.slice(0, level).join('.');
}

/**
 * Walks the document and builds a DecorationSet with one widget per heading.
 * The widget renders the chapter number prefix as a non-selectable span.
 */
function buildDecorations(doc: Node): DecorationSet {
  const decorations: Decoration[] = [];

  // Counters index 0..7 correspond to heading levels 1..8
  const counters = [0, 0, 0, 0, 0, 0, 0, 0];

  doc.forEach((node, offset) => {
    if (node.type.name !== 'heading') return;

    const level = node.attrs['level'] as number;
    if (typeof level !== 'number' || level < 1 || level > 8) return;

    // Increment this level's counter
    counters[level - 1]++;

    // Zero out all deeper levels
    for (let i = level; i < 8; i++) {
      counters[i] = 0;
    }

    const prefix = buildChapterPrefix(counters, level);

    // Widget decoration placed at the start of the heading node content (offset + 1)
    const widget = Decoration.widget(
      offset + 1,
      () => {
        const span = globalThis.document.createElement('span');
        span.className = 'chapter-number';
        span.contentEditable = 'false';
        span.textContent = `${prefix} `;
        return span;
      },
      { side: -1, key: `chapter-${offset}` },
    );

    decorations.push(widget);
  });

  return DecorationSet.create(doc, decorations);
}

/**
 * TipTap Extension that registers the chapter-numbering ProseMirror plugin.
 * Use as a standard TipTap extension in the editor's `extensions` array.
 * On every transaction, re-derives chapter numbers for all headings in document order.
 */
export const ChapterNumbering = Extension.create({
  name: 'chapterNumbering',

  addProseMirrorPlugins() {
    return [
      new Plugin({
        key: chapterNumberingKey,

        state: {
          init(_, { doc }) {
            return buildDecorations(doc);
          },
          apply(tr, _old) {
            // Rebuild on every transaction (cheap for typical document sizes)
            return buildDecorations(tr.doc);
          },
        },

        props: {
          decorations(state) {
            return chapterNumberingKey.getState(state) ?? DecorationSet.empty;
          },
        },
      }),
    ];
  },
});
