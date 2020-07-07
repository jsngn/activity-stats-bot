from unittest import mock
from unittest.mock import sentinel, MagicMock
import pytest

from tests.unit.test_extractor import stt

from bot import *
from requests.models import Response


@pytest.fixture
def cmt():
    # Valid summon
    cmt_1 = MagicMock()
    cmt_1.body = "!activitystatsbot ActivityStatsBot comments subreddit"
    cmt_1.id = "123abc"
    cmt_1.reply = MagicMock()

    # Invalid summon, wrong format, not enough info provided
    cmt_2 = MagicMock()
    cmt_2.body = "!activitystatsbot ActivityStatsBot"
    cmt_2.id = "abc123"
    cmt_2.reply = MagicMock()

    # Invalid summon, summon keyword absent
    cmt_3 = sentinel.Comment
    cmt_3.body = "activitystatsbot ActivityStatsBot comments subreddit"
    cmt_3.id = "def456"
    cmt_3.reply = MagicMock()

    # Invalid summon, format asking for illegal stats
    cmt_4 = MagicMock()
    cmt_4.body = "!activitystatsbot ActivityStatsBot upvotes awardcount"
    cmt_4.id = "789ghi"
    cmt_4.reply = MagicMock()

    return [cmt_1, cmt_2, cmt_3, cmt_4]


@pytest.fixture
def red(stt, cmt):
    """ Fixture of mock Reddit instance """

    red = sentinel.Reddit

    red.get = MagicMock(return_value=stt)
    red.subreddit = MagicMock()
    red.subreddit.return_value.comments = MagicMock(return_value=cmt)

    red.redditor = MagicMock()

    return sentinel.Reddit


@mock.patch("bot.requests.get")
@mock.patch("bot.add_comment")
def test_bot_integration(add_comment_mock, requests_get_mock, red, cmt):
    # Valid run where usernames exist, no comment IDs exist in db yet
    ids = {}
    red.redditor.return_value.id = MagicMock()
    res = Response()
    res._content = b'{"status": 200, "error": null, "response": [{"COUNT(*)": 0}]}'
    requests_get_mock.return_value = res

    run_bot(red, ids)

    assert len(ids) == add_comment_mock.call_count == len(cmt) - 1  # 1 comment that won't summon

    # Valid run where usernames exist, comment IDs exist in db but not in dict
    ids.clear()
    res._content = b'{"status": 200, "error": null, "response": [{"COUNT(*)": 1}]}'

    run_bot(red, ids)

    assert len(ids) == len(cmt) - 1

    # Valid run where usernames exist, DB returns error on GET request
    ids.clear()
    res._content = b'{"status": 500, "error": "some error", "response": null}'

    run_bot(red, ids)

    assert not ids


