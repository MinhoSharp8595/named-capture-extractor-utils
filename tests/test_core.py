"""Tests for named_capture_extractor_utils.

These tests exercise the behaviour the implementation actually claims:
- one key per named group, in declaration order
- non-participating groups map to None
- no match returns None
- extract_all returns a list of dictionaries
"""

import re
import unittest

from named_capture_extractor_utils import CompiledPattern, extract_named_groups


class TestExtractNamedGroups(unittest.TestCase):
    def test_basic_extraction(self):
        result = extract_named_groups(r"(?P<year>\d{4})-(?P<month>\d{2})", "2024-03")
        self.assertEqual(result, {"year": "2024", "month": "03"})

    def test_no_match_returns_none(self):
        result = extract_named_groups(r"(?P<year>\d{4})", "no year here")
        self.assertIsNone(result)

    def test_non_participating_group_is_none(self):
        # The (?:...) branch is not taken, so `optional` never participates.
        result = extract_named_groups(r"(?P<a>x)(?:y(?P<optional>z))?", "x")
        self.assertEqual(result, {"a": "x", "optional": None})

    def test_non_participating_group_is_none_when_branch_taken(self):
        result = extract_named_groups(r"(?P<a>x)(?:y(?P<optional>z))?", "xyz")
        self.assertEqual(result, {"a": "x", "optional": "z"})

    def test_empty_string_match(self):
        # An empty match is still a match; the group participates with "".
        result = extract_named_groups(r"(?P<everything>.*)", "")
        self.assertEqual(result, {"everything": ""})

    def test_unmatched_group_inside_alternation(self):
        result = extract_named_groups(r"(?:(?P<left>L)|(?P<right>R))", "R")
        self.assertEqual(result, {"left": None, "right": "R"})

    def test_flags_are_respected(self):
        result = extract_named_groups(r"(?P<word>hello)", "HELLO", re.IGNORECASE)
        self.assertEqual(result, {"word": "HELLO"})

    def test_invalid_pattern_raises(self):
        with self.assertRaises(re.error):
            extract_named_groups(r"(?P<unclosed", "anything")

    def test_duplicate_group_name_raises(self):
        with self.assertRaises(re.error):
            extract_named_groups(r"(?P<x>a)(?P<x>b)", "ab")

    def test_search_not_match(self):
        # The implementation uses search, so a substring match is enough.
        result = extract_named_groups(r"(?P<num>\d+)", "abc 42 def")
        self.assertEqual(result, {"num": "42"})


class TestCompiledPattern(unittest.TestCase):
    def test_compiled_extract(self):
        cp = CompiledPattern(r"(?P<key>\w+)=(?P<value>\w+)")
        self.assertEqual(cp.extract("a=1"), {"key": "a", "value": "1"})

    def test_compiled_extract_no_match(self):
        cp = CompiledPattern(r"(?P<key>\w+)=(?P<value>\w+)")
        self.assertIsNone(cp.extract("nope"))

    def test_group_names_order(self):
        cp = CompiledPattern(r"(?P<first>a)(?P<second>b)(?P<third>c)")
        self.assertEqual(cp.group_names(), ["first", "second", "third"])

    def test_group_names_empty(self):
        cp = CompiledPattern(r"no groups here")
        self.assertEqual(cp.group_names(), [])

    def test_extract_all(self):
        cp = CompiledPattern(r"(?P<digit>\d)")
        results = cp.extract_all("1 2 3")
        self.assertEqual(results, [{"digit": "1"}, {"digit": "2"}, {"digit": "3"}])

    def test_extract_all_no_matches(self):
        cp = CompiledPattern(r"(?P<digit>\d)")
        self.assertEqual(cp.extract_all("no digits"), [])

    def test_extract_all_with_non_participating(self):
        cp = CompiledPattern(r"(?P<a>x)(?P<b>y)?")
        self.assertEqual(cp.extract_all("x xy"), [{"a": "x", "b": None}, {"a": "x", "b": "y"}])

    def test_pattern_property(self):
        cp = CompiledPattern(r"(?P<n>\d+)")
        self.assertEqual(cp.pattern, r"(?P<n>\d+)")

    def test_compiled_pattern_reuse(self):
        cp = CompiledPattern(r"(?P<word>[a-z]+)")
        self.assertEqual(cp.extract("abc"), {"word": "abc"})
        self.assertEqual(cp.extract("xyz"), {"word": "xyz"})


if __name__ == "__main__":
    unittest.main()
