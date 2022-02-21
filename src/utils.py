from __future__ import annotations

class _MissingSentinel:
    def __eq__(self, other):
        return False

    def __bool__(self):
        return False

    def __repr__(self):
        return '...'

MISSING = _MissingSentinel()