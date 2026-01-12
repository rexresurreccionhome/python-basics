import pytest
from payment_system_with_retry.main import parse_args


def test_parse_args__with_required_arguments__returns_namespace(mocker):
    mocker.patch("sys.argv", ["main.py", "--state", "IL", "--amount", "100.00"])
    args = parse_args()
    assert args.state == "IL"
    assert args.amount == 100.00


def test_parse_args__missing_required_arguments__raises_system_exit(mocker):
    mocker.patch("sys.argv", ["main.py"])
    with pytest.raises(SystemExit) as exc_info:
        parse_args()
    assert exc_info.value.code == 2

