from typing import Dict, Any, List
from deepdiff import DeepDiff
import difflib

def generate_diff(data1: Dict[str, Any], data2: Dict[str, Any]) -> Dict[str, Any]:
    diff = DeepDiff(data1, data2, ignore_order=True, verbose_level=2)
    return compact_diff(diff)

def compact_diff(diff: Dict[str, Any]) -> Dict[str, Any]:
    compact = {}
    
    if 'values_changed' in diff:
        compact['changed'] = {}
        for path, change in diff['values_changed'].items():
            compact['changed'][path] = text_diff(str(change['old_value']), str(change['new_value']))
    
    if 'dictionary_item_added' in diff:
        compact['added'] = diff['dictionary_item_added']
    
    if 'dictionary_item_removed' in diff:
        compact['removed'] = diff['dictionary_item_removed']
    
    if 'type_changes' in diff:
        compact['type_changes'] = {}
        for path, change in diff['type_changes'].items():
            compact['type_changes'][path] = {
                'old_type': str(change['old_type']),
                'new_type': str(change['new_type']),
                'old_value': str(change['old_value']),
                'new_value': str(change['new_value'])
            }
    
    return compact

def text_diff(text1: str, text2: str) -> List[Dict[str, Any]]:
    """
    Generate a compact word-level diff between two strings.
    Returns a list of changes, where each change is a dict with keys:
    - 'type': 'added', 'removed', or 'replaced'
    - 'value': the word(s) that were changed
    - 'position': the position of the change in the original text (word index)
    """
    words1 = text1.split()
    words2 = text2.split()

    seqmatcher = difflib.SequenceMatcher(None, words1, words2)
    diff = []

    for opcode, i1, i2, j1, j2 in seqmatcher.get_opcodes():
        if opcode == 'insert':
            diff.append({'type': 'added', 'value': ' '.join(words2[j1:j2]), 'position': i1})
        elif opcode == 'delete':
            diff.append({'type': 'removed', 'value': ' '.join(words1[i1:i2]), 'position': i1})
        elif opcode == 'replace':
            diff.append({
                'type': 'replaced',
                'old_value': ' '.join(words1[i1:i2]),
                'new_value': ' '.join(words2[j1:j2]),
                'position': i1
            })

    return diff