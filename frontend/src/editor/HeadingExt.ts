/**
 * Custom Heading extension extending TipTap's built-in Heading to 8 levels.
 * StarterKit's Heading is capped at 1-6; this extension overrides the levels
 * config to support 1-8. Levels 7 and 8 render as <div class="heading-7/8">
 * since HTML only defines h1-h6 natively.
 */

import Heading from '@tiptap/extension-heading';
import type { Level } from '@tiptap/extension-heading';

/** All supported heading levels including the non-standard 7 and 8. */
export const HEADING_LEVELS: Level[] = [1, 2, 3, 4, 5, 6, 7, 8] as Level[];

/**
 * Extended Heading node supporting levels 1-8.
 * Levels 7-8 render as <div class="heading-7"> / <div class="heading-8"> since
 * HTML does not define h7/h8. Chapter numbering is applied via a ProseMirror
 * decoration plugin (ChapterNumbering.ts), not stored in the JSON.
 */
export const HeadingExt = Heading.extend({
  addOptions() {
    const parentOptions = this.parent?.() ?? { levels: [1, 2, 3, 4, 5, 6] as Level[], HTMLAttributes: {} };
    return {
      ...parentOptions,
      HTMLAttributes: parentOptions.HTMLAttributes ?? {},
      levels: HEADING_LEVELS,
    };
  },

  renderHTML({ node, HTMLAttributes }) {
    const level = node.attrs['level'] as number;
    if (level <= 6) {
      return [`h${level}`, HTMLAttributes, 0];
    }
    // h7 and h8: render as styled divs
    return ['div', { ...HTMLAttributes, class: `heading-${level}` }, 0];
  },

  parseHTML() {
    return HEADING_LEVELS.map((level) => {
      if (level <= 6) {
        return {
          tag: `h${level}`,
          attrs: { level },
        };
      }
      return {
        tag: `div.heading-${level}`,
        attrs: { level },
      };
    });
  },
});
