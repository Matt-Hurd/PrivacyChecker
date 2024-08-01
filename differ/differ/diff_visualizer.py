from typing import Dict, Any, List, Tuple

def visualize_diff(diff: Dict[str, Any]) -> str:
    output = []

    if 'values_changed' in diff:
        output.append("Values Changed:")
        for path, change in diff['values_changed'].items():
            output.append(f"  {path}:")
            output.append(visualize_text_diff(change))

    if 'dictionary_item_added' in diff:
        output.append("Items Added:")
        for item in diff['dictionary_item_added']:
            output.append(f"  + {item}")

    if 'dictionary_item_removed' in diff:
        output.append("Items Removed:")
        for item in diff['dictionary_item_removed']:
            output.append(f"  - {item}")

    if 'type_changes' in diff:
        output.append("Type Changes:")
        for path, change in diff['type_changes'].items():
            output.append(f"  {path}:")
            output.append(f"    From: {change['old_type']} ({change['old_value']})")
            output.append(f"    To:   {change['new_type']} ({change['new_value']})")

    if 'iterable_item_added' in diff:
        output.append("List Items Added:")
        for path, items in diff['iterable_item_added'].items():
            output.append(f"  {path}:")
            for item in items:
                output.append(f"    + {item}")

    if 'iterable_item_removed' in diff:
        output.append("List Items Removed:")
        for path, items in diff['iterable_item_removed'].items():
            output.append(f"  {path}:")
            for item in items:
                output.append(f"    - {item}")

    return "\n".join(output)

def visualize_text_diff(diff: List[Tuple[str, str]]) -> str:
    output = []
    current_line = []
    
    for change_type, word in diff:
        if change_type == ' ':
            current_line.append(word)
        elif change_type == '-':
            current_line.append(f"\033[91m{word}\033[0m")  # Red for removed
        elif change_type == '+':
            current_line.append(f"\033[92m{word}\033[0m")  # Green for added
        
        if len(' '.join(current_line)) > 80:  # Line wrap at 80 characters
            output.append('    ' + ' '.join(current_line))
            current_line = []
    
    if current_line:
        output.append('    ' + ' '.join(current_line))
    
    return '\n'.join(output)