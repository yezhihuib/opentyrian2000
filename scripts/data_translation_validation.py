#!/usr/bin/env python3
"""Shared source-bound structure checks for naturally reflowed Data prose."""


def validate_paragraphs(source_paragraphs, paragraphs, identity):
    """Allow prose splits/joins while retaining explicit source blank sentinels.

    Paragraph boundaries within a nonempty passage are editorial. An explicit
    empty source paragraph is a distinct separator, and bodyless occurrences
    must remain bodyless. Source identity and factual fidelity are separately
    pinned/reviewed; matching an old paragraph count cannot establish either.
    """
    if not isinstance(paragraphs, list) or not all(isinstance(p, str) for p in paragraphs):
        raise ValueError(f'{identity}: paragraphs must be a string array')
    if not source_paragraphs:
        if paragraphs:
            raise ValueError(f'{identity}: bodyless source occurrence gained content')
        return
    if any(p and not p.strip() for p in paragraphs):
        raise ValueError(f'{identity}: whitespace-only paragraph is not an explicit empty separator')

    def passages(values):
        result, has_content = [], False
        for value in values:
            if value.strip():
                has_content = True
            else:
                result.append(has_content)
                has_content = False
        return result + [has_content]

    if passages(source_paragraphs) != passages(paragraphs):
        raise ValueError(f'{identity}: missing content passage or changed explicit empty separators')
