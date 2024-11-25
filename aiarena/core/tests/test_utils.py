import pytest
from django.conf import settings

from aiarena.core.utils import parse_tags


@pytest.mark.parametrize(
    "input_tags,expected",
    [
        # Test empty inputs
        (None, []),
        ("", []),
        ([], []),
        # Test single tag
        ("tag1", ["tag1"]),
        (["tag1"], ["tag1"]),
        # Test multiple tags
        ("tag1,tag2", ["tag1", "tag2"]),
        (["tag1", "tag2"], ["tag1", "tag2"]),
        # Test whitespace handling
        (" tag1 , tag2 ", ["tag1", "tag2"]),
        ([" tag1 ", " tag2 "], ["tag1", "tag2"]),
        # Test case conversion
        ("TAG1,Tag2", ["tag1", "tag2"]),
        # Test newly added character handling (for - and :)
        ("tag-1,tag:2", ["tag-1", "tag:2"]),
        # Test regex cleaning
        ("tag#1,tag@2", ["tag1", "tag2"]),
        # Test length limit
        ("a" * (settings.MATCH_TAG_LENGTH_LIMIT + 1), ["a" * settings.MATCH_TAG_LENGTH_LIMIT]),
        # Test empty tags are removed
        ("tag1,,tag2", ["tag1", "tag2"]),
        # Test tag limit per match
        (",".join([f"tag{i}" for i in range(settings.MATCH_TAG_PER_MATCH_LIMIT + 1)]),
         [f"tag{i}" for i in range(settings.MATCH_TAG_PER_MATCH_LIMIT)]),
    ],
)
def test_parse_tags(input_tags, expected):
    """Test the parse_tags function handles various input cases correctly"""
    assert parse_tags(input_tags) == expected
