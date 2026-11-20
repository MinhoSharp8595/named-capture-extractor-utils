"""Named capture extractor utilities.

Exports the public API: ``extract_named_groups`` and ``CompiledPattern``.
"""

from .core import CompiledPattern, extract_named_groups

__all__ = ["CompiledPattern", "extract_named_groups"]
