from typing import Dict, Any, List, Tuple
from deepdiff import DeepDiff
import difflib

def generate_diff(data1: Dict[str, Any], data2: Dict[str, Any]) -> Dict[str, Any]:
    diff = DeepDiff(data1, data2, ignore_order=True, verbose_level=2)
    refined_diff = refine_diff(diff)
    return refined_diff

def refine_diff(diff: Dict[str, Any]) -> Dict[str, Any]:
    refined = {}
    
    if 'values_changed' in diff:
        refined['values_changed'] = {}
        for path, change in diff['values_changed'].items():
            old_value = str(change['old_value'])
            new_value = str(change['new_value'])
            refined['values_changed'][path] = text_diff(old_value, new_value)
    
    # Handle other types of changes
    for key in ['dictionary_item_added', 'dictionary_item_removed', 'type_changes',
                'iterable_item_added', 'iterable_item_removed']:
        if key in diff:
            refined[key] = diff[key]
    
    return refined

def text_diff(text1: str, text2: str) -> List[Tuple[str, str]]:
    """
    Generate a word-level diff between two strings.
    Returns a list of tuples: (change_type, word)
    where change_type is '+' for added, '-' for removed, or ' ' for unchanged.
    """
    def split_words(text):
        return text.split()

    words1 = split_words(text1)
    words2 = split_words(text2)

    seqmatcher = difflib.SequenceMatcher(None, words1, words2)
    diff = []

    for opcode, i1, i2, j1, j2 in seqmatcher.get_opcodes():
        if opcode == 'equal':
            diff.extend([(' ', word) for word in words1[i1:i2]])
        elif opcode == 'delete':
            diff.extend([('-', word) for word in words1[i1:i2]])
        elif opcode == 'insert':
            diff.extend([('+', word) for word in words2[j1:j2]])
        elif opcode == 'replace':
            diff.extend([('-', word) for word in words1[i1:i2]])
            diff.extend([('+', word) for word in words2[j1:j2]])

    return diff