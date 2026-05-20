/**
 * TypeScript types mirroring the backend Pydantic schemas.
 * All string-literal union types match backend enum values exactly.
 */

/** Allowed status values for a requirement. */
export type RequirementStatus =
  | 'draft'
  | 'in_review'
  | 'wait_for_approval'
  | 'approved'
  | 'expired';

/** Allowed requirement type values. */
export type RequirementType =
  | 'customer_requirement'
  | 'system_requirement'
  | 'software_requirement'
  | 'hardware_requirement';

/** Allowed link type values. */
export type LinkType = 'refines' | 'depends_on' | 'tested_by';

/** A link side can point at either a Requirement or a Testcase. */
export type LinkSideKind = 'requirement' | 'testcase';

/** Compact representation of one side of a link — kind plus identifying fields. */
export interface LinkSide {
  kind: LinkSideKind;
  id: number;
  project_id: string;
  title: string;
}

/** One entry in the list_of_links on a requirement detail response. */
export interface LinkItem {
  link_id: number;
  link_type: string;
  start_project_id: string;
  destination_project_id: string;
  other_side: LinkSide;
}

/** List-view projection of a requirement (GET /api/requirements). */
export interface RequirementSummary {
  id: number;
  project_id: string;
  title: string;
  status: string;
  requirement_type: string;
  last_edited_on: string;
}

/** Full requirement detail including resolved list_of_links. */
export interface RequirementDetail {
  id: number;
  requirement_number: number;
  project_id: string;
  title: string;
  description: string;
  status: string;
  requirement_type: string;
  author: string;
  last_edited_by: string;
  created_on: string;
  last_edited_on: string;
  revision: string;
  list_of_links: LinkItem[];
}

/** Response from POST /api/requirements/reserve-id. */
export interface ReserveIdOut {
  requirement_number: number;
  project_id: string;
}

/** Body for POST /api/requirements. */
export interface RequirementCreateBody {
  requirement_number: number;
  project_id: string;
  title: string;
  description: string;
  status: RequirementStatus;
  requirement_type: RequirementType;
  revision: string;
}

/** Body for PUT /api/requirements/:id. */
export interface RequirementUpdateBody {
  title: string;
  description: string;
  status: RequirementStatus;
  requirement_type: RequirementType;
  revision: string;
}

/** Full link object returned by POST /api/links. */
export interface LinkOut {
  id: number;
  project_id: string;
  link_type: string;
  link_start_kind: LinkSideKind;
  link_start: number;
  link_destination_kind: LinkSideKind;
  link_destination: number;
  created_on: string;
  last_edited_on: string;
}

/** Body for POST /api/links. */
export interface LinkCreateBody {
  link_type: LinkType;
  link_start_project_id: string;
  link_destination_project_id: string;
}

/** Human-readable labels for requirement status values. */
export const STATUS_LABELS: Record<RequirementStatus, string> = {
  draft: 'Draft',
  in_review: 'In Review',
  wait_for_approval: 'Wait for Approval',
  approved: 'Approved',
  expired: 'Expired',
};

/** Human-readable labels for requirement type values. */
export const TYPE_LABELS: Record<RequirementType, string> = {
  customer_requirement: 'Customer Requirement',
  system_requirement: 'System Requirement',
  software_requirement: 'Software Requirement',
  hardware_requirement: 'Hardware Requirement',
};

/** Human-readable labels for link type values. */
export const LINK_TYPE_LABELS: Record<LinkType, string> = {
  refines: 'Refines',
  depends_on: 'Depends On',
  tested_by: 'Tested By',
};

/** All valid status values in order for use in dropdowns. */
export const STATUS_VALUES: RequirementStatus[] = [
  'draft',
  'in_review',
  'wait_for_approval',
  'approved',
  'expired',
];

/** All valid requirement type values in order for use in dropdowns. */
export const TYPE_VALUES: RequirementType[] = [
  'customer_requirement',
  'system_requirement',
  'software_requirement',
  'hardware_requirement',
];

/** All valid link type values in order for use in dropdowns. */
export const LINK_TYPE_VALUES: LinkType[] = ['refines', 'depends_on', 'tested_by'];
