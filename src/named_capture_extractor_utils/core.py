"""Core implementation for extracting named capture groups.

The module deliberately uses Python's built-in re module. A single decision
drives the API: when a named group does not participate in the match, we return
``None`` for that key rather than omitting it. That makes the shape of the result
depend only on the pattern, not on the input, which is easier to reason about
when the dictionary is consumed downstream.
"""

from __future__ import annotations

import re
from typing import Dict, Optional, Pattern

__all__ = ["CompiledPattern", "extract_named_groups"]


class CompiledPattern:
    """A thin wrapper around a compiled regular expression.

    The wrapper exists so callers can compile once and extract many times
    without recompiling, while still getting the same dictionary shape as
    :func:`extract_named_groups`.
    """

    __slots__ = ("_pattern",)

    def __init__(self, pattern: str, flags: int = 0) -> None:
        """Compile *pattern* with the given *flags*.

        Raises
        ------
        re.error
            If the pattern is invalid or contains a named group that is not a
            valid Python identifier, or duplicate group names.
        """
        self._pattern: Pattern[str] = re.compile(pattern, flags)

    @property
    def pattern(self) -> str:
        """The original pattern string."""
        return self._pattern.pattern

    def group_names(self) -> list[str]:
        """Return the names of all capture groups, in declaration order.

        The order follows the order the groups appear in the pattern, which is
        what ``re`` reports. This is stable and independent of the input.
        """
        return list(self._pattern.groupindex.keys())

    def extract(self, text: str) -> Optional[Dict[str, Optional[str]]]:
        """Run the pattern against *text*.

        Returns a dictionary mapping every named group to its matched string,
        or ``None`` for groups that did not participate. Returns ``None`` when
        the pattern does not match at all.
        """
        match = self._pattern.search(text)
        if match is None:
            return None
        return _match_to_dict(match, self._pattern)

    def extract_all(self, text: str) -> list[Dict[str, Optional[str]]]:
        """Run the pattern against *text* and return every non-overlapping match.

        Each element is a dictionary with the same keys as :meth:`extract`.
        Returns an empty list when there are no matches.
        """
        return [_match_to_dict(m, self._pattern) for m in self._pattern.finditer(text)]


def _match_to_dict(match: re.Match[str], pattern: Pattern[str]) -> Dict[str, Optional[str]]:
    """Convert a match object into a name -> value dictionary.

    Every named group in *pattern* appears as a key. Groups that did not
    participate map to ``None``.
    """
    result: Dict[str, Optional[str]] = {}
    for name in pattern.groupindex:
        result[name] = match.group(name)
    return result


def extract_named_groups(
    pattern: str,
    text: str,
    flags: int = 0,
) -> Optional[Dict[str, Optional[str]]]:
    """Compile *pattern* and return named capture groups from *text*.

    This is the one-shot convenience function. For repeated use, prefer
    :class:`CompiledPattern` to avoid recompiling.

    Parameters
    ----------
    pattern:
        A regular expression string. Named groups use the ``(?P<name>...)``
        syntax.
    text:
        The string to search.
    flags:
        Optional ``re`` flags, e.g. ``re.IGNORECASE``.

    Returns
    -------
    dict or None
        A dictionary with one key per named group. Groups that did not
        participate in the match have value ``None``. Returns ``None`` if the
        pattern does not match.
    """
    compiled = CompiledPattern(pattern, flags)
    return compiled.extract(text)
