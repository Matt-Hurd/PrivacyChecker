export interface Change {
  type: 'added' | 'removed' | 'replaced';
  value?: string;
  old_value?: string;
  new_value?: string;
  position: number;
}

export interface DiffContent {
  changed: Record<string, Change[]>;
  added: string[];
  removed: string[];
  type_changes: Record<string, {
    old_type: string;
    new_type: string;
    old_value: any;
    new_value: any;
  }>;
}

export interface DiffSummary {
  total_changes: number;
  added: number;
  removed: number;
  changed: number;
  type_changes: number;
}

export interface Diff {
  id: string;
  company: string;
  from_version: string;
  to_version: string;
  diff: DiffContent;
  summary: DiffSummary;
}