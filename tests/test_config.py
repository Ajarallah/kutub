
import pytest

from kutub import config
from kutub.cli import build_parser


@pytest.fixture(autouse=True)
def isolated_home(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "HOME", tmp_path)
    monkeypatch.setattr(config, "CONFIG_PATH", tmp_path / "config.json")
    monkeypatch.delenv("TG_API_ID", raising=False)
    monkeypatch.delenv("TG_API_HASH", raising=False)


def test_load_returns_empty_when_absent():
    assert config.load() == {}


def test_save_then_load_roundtrip():
    config.save({"api_id": "1", "api_hash": "abc"})
    assert config.load()["api_hash"] == "abc"


def test_saved_config_is_owner_readable_only():
    config.save({"api_id": "1"})
    assert config.CONFIG_PATH.stat().st_mode & 0o077 == 0


def test_malformed_config_does_not_raise():
    config.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    config.CONFIG_PATH.write_text("{not json")
    assert config.load() == {}


def test_environment_overrides_config_file(monkeypatch):
    config.save({"api_id": "from_file", "api_hash": "from_file"})
    monkeypatch.setenv("TG_API_ID", "from_env")
    monkeypatch.setenv("TG_API_HASH", "from_env")
    assert config.credentials() == ("from_env", "from_env")


def test_missing_credentials_exit_with_guidance():
    with pytest.raises(SystemExit) as excinfo:
        config.credentials()
    assert "my.telegram.org" in str(excinfo.value)


def test_download_dir_is_created(tmp_path):
    target = tmp_path / "nested" / "downloads"
    assert config.download_dir(str(target)).exists()


def test_ebook_extensions_cover_common_formats():
    assert {".epub", ".pdf", ".mobi"} <= config.EBOOK_EXTENSIONS


@pytest.mark.parametrize(
    "argv",
    [
        ["search", "dune"],
        ["list", "-n", "5"],
        ["stats"],
        ["index", "@channel"],
        ["get", "1", "--kindle"],
        ["channels"],
        ["login"],
    ],
)
def test_parser_accepts_documented_commands(argv):
    assert build_parser().parse_args(argv).handler is not None


def test_parser_requires_a_command():
    with pytest.raises(SystemExit):
        build_parser().parse_args([])


def test_get_requires_integer_id():
    with pytest.raises(SystemExit):
        build_parser().parse_args(["get", "not-a-number"])


def test_search_default_limit():
    assert build_parser().parse_args(["search", "dune"]).n == 25
