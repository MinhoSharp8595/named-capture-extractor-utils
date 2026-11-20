# named-capture-extractor-utils

Run a regular expression against text and get back a dictionary of named capture groups and their matches.

```python
from named_capture_extractor_utils import extract_named_groups

result = extract_named_groups(
    r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})",
    "Date: 2024-03-15",
)
print(result)
# {'year': '2024', 'month': '03', 'day': '15'}
```

For repeated use, compile once with `CompiledPattern`:

```python
from named_capture_extractor_utils import CompiledPattern

pattern = CompiledPattern(r"(?P<key>\w+)=(?P<value>\w+)")
print(pattern.extract("a=1"))
# {'key': 'a', 'value': '1'}

print(pattern.extract_all("a=1 b=2"))
# [{'key': 'a', 'value': '1'}, {'key': 'b', 'value': '2'}]
```

## Why this exists

Python's `re` module already exposes named groups through `match.groupdict()`, but that method only includes groups that appear in the pattern's group index and silently drops groups that did not participate in the match. The shape of the result therefore changes with the input, which is awkward when the dictionary is passed to code that expects a fixed set of keys.

This library makes one deliberate choice: **every named group in the pattern is always present in the returned dictionary**. A group that did not participate maps to `None`. The dictionary shape is determined solely by the pattern, so downstream code can rely on the keys without first inspecting the match object.

The trade-off is that callers who want to distinguish "group absent from pattern" from "group present but unmatched" must do so by inspecting the pattern, not the result. In practice, patterns are fixed at compile time and this distinction is rarely useful.

## The awkward edge

When the pattern does not match at all, `extract_named_groups` returns `None`, not an empty dictionary. This is intentional: an empty dictionary would be indistinguishable from a successful match where every group is empty, and the two situations usually need different handling. `CompiledPattern.extract` follows the same convention. `CompiledPattern.extract_all` returns an empty list when there are no matches, since a list naturally represents "zero or more matches".

## API

- `extract_named_groups(pattern: str, text: str, flags: int = 0) -> dict[str, str | None] | None`
  Compile `pattern` and return the named groups from the first match in `text`. Returns `None` if there is no match.

- `CompiledPattern(pattern: str, flags: int = 0)`
  Compile once, extract many times.
  - `.extract(text: str) -> dict[str, str | None] | None`
  - `.extract_all(text: str) -> list[dict[str, str | None]]`
  - `.group_names() -> list[str]`
  - `.pattern` (property) returns the original pattern string.

Named groups use the `(?P<name>...)` syntax. Duplicate names and invalid patterns raise `re.error`, matching the behaviour of the standard library.
