import types
import importlib
from unittest import mock
import datetime

import pytest

# Note: Testing framework: pytest (using pytest style tests and monkeypatch fixtures)

def _import_bot_module(monkeypatch):
    """
    Try to import the target module that contains the functions under test.
    Search order:
      - bot
      - application.bot
      - tests.test_bot  (as per provided snippet path)
    Also neutralize locale.setlocale at import time to avoid environment-specific failures.
    """
    # Ensure locale.setlocale doesn't fail at import
    with mock.patch("locale.setlocale", return_value=None):
        for name in ("bot", "application.bot", "tests.test_bot"):
            try:
                mod = importlib.import_module(name)
                # Check for one key function to confirm
                if hasattr(mod, "pogibli") and hasattr(mod, "postradali"):
                    return mod
            except Exception:
                continue
    pytest.skip("Could not locate module containing bot functions (pogibli, postradali, etc.).")

@pytest.fixture
def bot(monkeypatch):
    return _import_bot_module(monkeypatch)

# -------------------------
# Pure function tests: pogibli
# -------------------------
@pytest.mark.parametrize(
    "num,expected",
    [
        ("0", "погибли"),
        ("1", "погиб"),     # endswith 1 and not 11
        ("2", "погибли"),
        ("4", "погибли"),
        ("5", "погибли"),
        ("10", "погибли"),
        ("11", "погибли"),  # special-case teens
        ("21", "погиб"),
        ("31", "погиб"),
        ("101", "погиб"),
        ("111", "погибли"),
        ("1001", "погиб"),
    ],
)
def test_pogibli_russian_pluralization(num, expected, bot):
    assert bot.pogibli(num) == expected

# -------------------------
# Pure function tests: postradali
# -------------------------
@pytest.mark.parametrize(
    "num,expected",
    [
        ("0", "пострадали"),
        ("1", "пострадал"),
        ("2", "пострадали"),
        ("11", "пострадали"),
        ("21", "пострадал"),
        ("101", "пострадал"),
        ("111", "пострадали"),
    ],
)
def test_postradali_russian_pluralization(num, expected, bot):
    assert bot.postradali(num) == expected

# -------------------------
# get_word_form with pymorphy2 mocked
# -------------------------
def test_get_word_form_uses_pymorphy2(bot, monkeypatch):
    # Prepare a mock MorphAnalyzer that returns a mock parse result with make_agree_with_number
    mock_parse_result = mock.Mock()
    mock_parse_result.make_agree_with_number.return_value = mock.Mock(word="людей")
    mock_morph = mock.Mock()
    mock_morph.parse.return_value = [mock_parse_result]

    with mock.patch.object(bot.pymorphy2, "MorphAnalyzer", return_value=mock_morph):
        # "людей" is specifically converted to "человек" by the function
        assert bot.get_word_form("человек", "2") == "человек"
        # Ensure it called parse with the word and make_agree_with_number with int(number)
        mock_morph.parse.assert_called_once_with("человек")
        mock_parse_result.make_agree_with_number.assert_called_once_with(2)

def test_get_word_form_other_forms(bot, monkeypatch):
    # For non-людей result, it should just return the resulting word
    mock_parse_result = mock.Mock()
    mock_parse_result.make_agree_with_number.return_value = mock.Mock(word="человека")
    mock_morph = mock.Mock()
    mock_morph.parse.return_value = [mock_parse_result]

    with mock.patch.object(bot.pymorphy2, "MorphAnalyzer", return_value=mock_morph):
        assert bot.get_word_form("человек", "1") == "человека"

# -------------------------
# generate_text tests with pymorphy2 mocked and deterministic date
# -------------------------
def test_generate_text_today_post(bot, monkeypatch):
    data = {
        "string_date": "1 января",
        "weekday": "понедельник",
        "crashes_deaths": "1",
        "date": datetime.date(2024, 1, 1),  # not used in today_post
    }
    # get_word_form returns "человек" for "1"
    monkeypatch.setattr(bot, "get_word_form", lambda w, n: "человек")
    monkeypatch.setattr(bot, "pogibli", lambda n: "погиб")
    out = bot.generate_text(data, "today_post")
    assert "1 января, понедельник" in out
    assert "в ДТП погиб 1 человек" in out

def test_generate_text_week_post(bot, monkeypatch):
    data = {
        "string_date": "irrelevant",
        "weekday": "irrelevant",
        "crashes_deaths": "5",
        "date": datetime.date(2024, 1, 2),
    }
    monkeypatch.setattr(bot, "get_word_form", lambda w, n: "человек")
    monkeypatch.setattr(bot, "pogibli", lambda n: "погибли")
    out = bot.generate_text(data, "week_post")
    assert out.startswith("За последнюю неделю")
    assert "в ДТП погибли 5 человек" in out

def test_generate_text_month_post(bot, monkeypatch):
    data = {
        "string_date": "irrelevant",
        "weekday": "irrelevant",
        "crashes_deaths": "21",
        "date": datetime.date(2024, 2, 1),
    }
    # Mock pymorphy2 to supply nominative month word
    mock_parsed = mock.Mock()
    mock_parsed.inflect.return_value = mock.Mock(word="февраль")
    mock_morph = mock.Mock()
    mock_morph.parse.return_value = [mock_parsed]

    with mock.patch.object(bot.pymorphy2, "MorphAnalyzer", return_value=mock_morph):
        monkeypatch.setattr(bot, "get_word_form", lambda w, n: "человек")
        monkeypatch.setattr(bot, "pogibli", lambda n: "погиб")
        out = bot.generate_text(data, "month_post")
        assert out.startswith("За февраль")
        assert "в ДТП погиб 21 человек" in out

# -------------------------
# get_today_data tests: mock requests, BeautifulSoup document, and Django update_or_create
# -------------------------
def _fake_html(date_str="01.01.2024"):
    # Construct the minimal HTML structure expected by the parser:
    # table.b-crash-stat > th contains date, then rows for metrics
    # order:
    #   [1] crashes_num
    #   [2] crashes_deaths
    #   [3] crashes_child_deaths
    #   [4] crashes_injured
    #   [5] crashes_child_injured
    rows = [
        ('ДТП', '100'),
        ('Погибшие', '10'),
        ('Погибшие дети', '1'),
        ('Раненые', '50'),
        ('Раненые дети', '5'),
    ]
    body_rows = "".join(
        f"<tr><td>{name}</td><td>{val}</td></tr>"
        for name, val in rows
    )
    html = f"""
    <html>
      <body>
        <table class="b-crash-stat">
          <thead>
            <tr><th>Статистика за {date_str}</th></tr>
          </thead>
          <tbody>
            {body_rows}
          </tbody>
        </table>
      </body>
    </html>
    """
    return html

def test_get_today_data_parses_and_updates_db(bot, monkeypatch):
    # Mock requests.get
    fake_resp = types.SimpleNamespace(text=_fake_html("02.03.2024"))
    monkeypatch.setattr(bot.requests, "get", lambda *a, **k: fake_resp)

    # Mock env('PROXY') returning empty so proxies https: None
    fake_env = mock.Mock()
    fake_env.__call__ = mock.Mock(return_value="")
    # Patch the env used in the module
    monkeypatch.setattr(bot, "env", fake_env, raising=True)

    # Mock models.BriefData.objects.update_or_create
    update_or_create_mock = mock.Mock(return_value=(object(), True))
    class _Objects:
        def update_or_create(self, **kwargs):
            return update_or_create_mock(**kwargs)
    class _BriefData:
        objects = _Objects()
    monkeypatch.setattr(bot.models, "BriefData", _BriefData)

    data = bot.get_today_data()

    # Validate date parsing and fields
    assert data["date"] == datetime.date(2024, 3, 2)
    assert isinstance(data["weekday"], str)
    assert data["string_date"]  # non-empty localized date text
    assert data["crashes_num"] == "100"
    assert data["crashes_deaths"] == "10"
    assert data["crashes_child_deaths"] == "1"
    assert data["crashes_injured"] == "50"
    assert data["crashes_child_injured"] == "5"

    # Validate DB update_or_create call structure
    update_or_create_mock.assert_called_once()
    call_kwargs = update_or_create_mock.call_args.kwargs
    assert call_kwargs["date"] == datetime.date(2024, 3, 2)
    defaults = call_kwargs["defaults"]
    assert defaults == {
        "dtp_count": "100",
        "death_count": "10",
        "injured_count": "50",
        "child_death_count": "1",
        "child_injured_count": "5",
    }

# -------------------------
# make_img tests: mock PIL to avoid file I/O and environment dependencies
# -------------------------
class _DummyImage:
    def __init__(self, size=(100, 100)):
        self._size = size
    def convert(self, mode):
        return self
    @property
    def size(self):
        return self._size
    def resize(self, new_size, resample=None):
        return _DummyImage(size=new_size)
    def paste(self, *a, **k):
        pass
    def save(self, path):
        # validate the path ends with img.png
        assert path.endswith("img.png")

class _DummyDraw:
    def __init__(self, img):
        pass
    def textsize(self, text, font=None):
        # Return width proportional to string length for positioning
        return (10 * len(str(text)), 10)
    def text(self, *a, **k):
        pass
    def rectangle(self, *a, **k):
        pass

def test_make_img_calls_pil_and_saves(bot, monkeypatch, tmp_path):
    # Patch __file__ directory to a temp dir where template assets "exist"
    # We'll avoid actually opening files by mocking Image.open and ImageFont.truetype.
    fake_dir = tmp_path
    fake_file = fake_dir / "module.py"
    fake_file.write_text("# dummy")
    # Monkeypatch module __file__ (path used for locating resources)
    monkeypatch.setattr(bot, "__file__", str(fake_file))

    # Mock PIL components
    monkeypatch.setattr(bot.Image, "open", lambda *_args, **_kwargs: _DummyImage())
    monkeypatch.setattr(bot.Image, "ANTIALIAS", 1, raising=False)
    monkeypatch.setattr(bot.ImageFont, "truetype", lambda *a, **k: object())
    monkeypatch.setattr(bot.ImageDraw, "Draw", _DummyDraw)

    # Prepare input data
    data = {
        "crashes_deaths": "12",
        "string_date": "2 марта",
        "date": datetime.date(2024, 3, 2),
    }

    bot.make_img(data)  # Should not raise and should attempt to save

# -------------------------
# send_tweet tests: mock tweepy OAuth and API calls
# -------------------------
def test_send_tweet_uploads_media_and_posts(bot, monkeypatch, tmp_path):
    # Arrange environment via env() call pattern and os.path for img.png
    img = tmp_path / "img.png"
    img.write_bytes(b"fake image bytes")
    monkeypatch.setattr(bot, "__file__", str(img))  # so dirname(...)/img.png resolves to tmp path
    # Mock env accessor
    def fake_env(key):
        mapping = {
            "TWITTER_CONSUMER_KEY": "ck",
            "TWITTER_CONSUMER_SECRET": "cs",
            "TWITTER_CONSUMER_TOKEN": "at",
            "TWITTER_CONSUMER_TOKEN_SECRET": "ats",
        }
        return mapping[key]
    monkeypatch.setattr(bot, "env", fake_env, raising=True)

    # Mock tweepy OAuth and APIs
    mock_api = mock.Mock()
    mock_client = mock.Mock()
    class _SimpleUploadResult:
        media_id = 12345

    def fake_OAuthHandler(ck, cs):
        return object()
    monkeypatch.setattr(bot.tweepy, "OAuthHandler", fake_OAuthHandler)
    monkeypatch.setattr(bot.tweepy, "API", lambda auth: mock_api)
    monkeypatch.setattr(bot.tweepy, "Client", lambda **kw: mock_client)

    # simple_upload returns an object with media_id
    mock_api.simple_upload.return_value = _SimpleUploadResult()

    bot.send_tweet("hello")
    mock_api.simple_upload.assert_called_once()
    mock_api.create_media_metadata.assert_called_once_with(media_id=12345, alt_text="")
    mock_client.create_tweet.assert_called_once()
    args, kwargs = mock_client.create_tweet.call_args
    assert kwargs["text"] == "hello"
    assert kwargs["media_ids"] == [12345]

# -------------------------
# send_telegram_post tests: mock telegram.Bot and channel iteration
# -------------------------
def test_send_telegram_post_sends_to_channels(bot, monkeypatch, tmp_path, capsys):
    # Prepare image file
    img = tmp_path / "img.png"
    img.write_bytes(b"fake")
    monkeypatch.setattr(bot, "__file__", str(img))

    # Mock env('TELEGRAM_TOKEN')
    monkeypatch.setenv("TELEGRAMM_CHANNELS", " @ch1 ;@ch2;  ; ")
    def fake_env(key):
        return "token-value"
    monkeypatch.setattr(bot, "env", fake_env, raising=True)

    # Mock telegram.Bot
    mock_bot = mock.Mock()
    monkeypatch.setattr(bot.telegram, "Bot", lambda token: mock_bot)

    bot.send_telegram_post("caption text")

    # Should sendPhoto to both channels
    assert mock_bot.sendPhoto.call_count == 2
    calls = [call.args[0] for call in mock_bot.sendPhoto.call_args_list]
    assert calls == ["@ch1", "@ch2"]

    # Printouts include helpful messages
    out, _ = capsys.readouterr()
    assert "TELEGRAMM_CHANNELS" in out
    assert "Успешно отправлено" in out

def test_send_telegram_post_handles_errors(bot, monkeypatch, tmp_path, capsys):
    # Prepare image file
    img = tmp_path / "img.png"
    img.write_bytes(b"fake")
    monkeypatch.setattr(bot, "__file__", str(img))

    monkeypatch.setenv("TELEGRAMM_CHANNELS", "@ok;@fail")
    def fake_env(key):
        return "token-value"
    monkeypatch.setattr(bot, "env", fake_env, raising=True)

    class _Bot:
        def sendPhoto(self, channel, photo, caption):
            if channel == "@fail":
                raise RuntimeError("boom")
    monkeypatch.setattr(bot.telegram, "Bot", lambda token: _Bot())

    bot.send_telegram_post("txt")
    out, _ = capsys.readouterr()
    assert "Ошибка при отправке" in out

# -------------------------
# main flow tests: gating by SEND_* env vars, invoking side-effect functions
# -------------------------
def test_main_today_calls_expected_flows(bot, monkeypatch, capsys):
    # Mock get_today_data to return minimal valid data
    data = {
        "string_date": "1 января",
        "weekday": "понедельник",
        "crashes_deaths": "1",
        "crashes_child_deaths": "0",
        "crashes_injured": "2",
        "crashes_child_injured": "0",
        "crashes_num": "3",
        "date": datetime.date(2024, 1, 1),
    }
    monkeypatch.setattr(bot, "get_today_data", lambda: data)
    monkeypatch.setattr(bot, "generate_text", lambda d, t: "TEXT")
    mock_make_img = mock.Mock()
    monkeypatch.setattr(bot, "make_img", mock_make_img)

    # Gate all sends off by default
    monkeypatch.delenv("SEND_TWEETER", raising=False)
    monkeypatch.delenv("SEND_TELEGRAM", raising=False)
    monkeypatch.delenv("SEND_VK", raising=False)

    # Mock senders to verify they are not called
    mock_send_tweet = mock.Mock()
    mock_send_tg = mock.Mock()
    monkeypatch.setattr(bot, "send_tweet", mock_send_tweet)
    monkeypatch.setattr(bot, "send_telegram_post", mock_send_tg)
    # send_vk_post may not exist; mock safely if present
    if hasattr(bot, "send_vk_post"):
        monkeypatch.setattr(bot, "send_vk_post", mock.Mock())

    bot.main("today")
    out, _ = capsys.readouterr()

    # Ensure text generated and image created
    mock_make_img.assert_called_once_with(data)
    assert "[main] Получены данные: True" in out

    # Ensure no sends happened
    mock_send_tweet.assert_not_called()
    mock_send_tg.assert_not_called()

def test_main_today_sends_when_env_set(bot, monkeypatch):
    data = {
        "string_date": "1 января",
        "weekday": "понедельник",
        "crashes_deaths": "1",
        "crashes_child_deaths": "0",
        "crashes_injured": "2",
        "crashes_child_injured": "0",
        "crashes_num": "3",
        "date": datetime.date(2024, 1, 1),
    }
    monkeypatch.setattr(bot, "get_today_data", lambda: data)
    monkeypatch.setattr(bot, "generate_text", lambda d, t: "TEXT")

    mock_make_img = mock.Mock()
    mock_send_tweet = mock.Mock()
    mock_send_tg = mock.Mock()
    monkeypatch.setattr(bot, "make_img", mock_make_img)
    monkeypatch.setattr(bot, "send_tweet", mock_send_tweet)
    monkeypatch.setattr(bot, "send_telegram_post", mock_send_tg)

    monkeypatch.setenv("SEND_TWEETER", "1")
    monkeypatch.setenv("SEND_TELEGRAM", "1")
    monkeypatch.setenv("SEND_VK", "0")  # ensure VK path not taken

    # If send_vk_post exists, ensure it's not called
    if hasattr(bot, "send_vk_post"):
        mock_send_vk = mock.Mock()
        monkeypatch.setattr(bot, "send_vk_post", mock_send_vk)

    bot.main("today")

    mock_make_img.assert_called_once_with(data)
    mock_send_tweet.assert_called_once_with("TEXT")
    mock_send_tg.assert_called_once_with("TEXT")
    if hasattr(bot, "send_vk_post"):
        mock_send_vk.assert_not_called()

# Edge case: get_today_data returns falsy (None) leads to no further action
def test_main_today_no_data(bot, monkeypatch, capsys):
    monkeypatch.setattr(bot, "get_today_data", lambda: None)
    bot.main("today")
    out, _ = capsys.readouterr()
    assert "[main] Получены данные: False" in out