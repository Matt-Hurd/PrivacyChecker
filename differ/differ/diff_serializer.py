from typing import Dict, Any, List

def serialize_diff(diff: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize the diff into a compact JSON representation.
    """
    return diff  # The diff is already in a compact form, so we just return it as is

def generate_diff_summary(diff: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a summary of the diff, including statistics and a preview.
    """
    summary = {
        'total_changes': 0,
        'added': 0,
        'removed': 0,
        'changed': 0,
        'type_changes': 0,
        'preview': []
    }

    if 'changed' in diff:
        summary['changed'] = len(diff['changed'])
        summary['total_changes'] += summary['changed']
        
        # Add a preview of the first few changes
        for path, changes in list(diff['changed'].items())[:5]:
            summary['preview'].append({
                'path': path,
                'sample': changes[:3]  # First 3 diff items as a sample
            })

    if 'added' in diff:
        summary['added'] = len(diff['added'])
        summary['total_changes'] += summary['added']

    if 'removed' in diff:
        summary['removed'] = len(diff['removed'])
        summary['total_changes'] += summary['removed']

    if 'type_changes' in diff:
        summary['type_changes'] = len(diff['type_changes'])
        summary['total_changes'] += summary['type_changes']

    return summary