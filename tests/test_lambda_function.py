import pytest

from src.lambda_function import parse_params


@pytest.mark.parametrize(
    ("param", "expected"),
    [
        (None, None),
        ("", None),
        ("text=a", ["a"]),
        ("text=a b", ["a", "b"]),
    ],
)
def test_parse_params(param, expected):
    assert parse_params(param) == expected
