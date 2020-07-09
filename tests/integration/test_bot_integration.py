""" Integration testing for activity stats bot
    Josephine Nguyen, 2020 """

from unittest import mock
from unittest.mock import sentinel, MagicMock
import pytest


from tests.unit.test_extractor import stt
from bot import *
from requests.models import Response


@pytest.fixture
def cmt():
    """ Fixture of mock comments that attempt to summon activity stats bot """

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

    # Invalid summon, format asking for illegal stats
    cmt_3 = MagicMock()
    cmt_3.body = "!activitystatsbot ActivityStatsBot upvotes awardcount"
    cmt_3.id = "789ghi"
    cmt_3.reply = MagicMock()

    # Invalid summon, summon keyword absent
    cmt_4 = sentinel.Comment
    cmt_4.body = "activitystatsbot ActivityStatsBot comments subreddit"
    cmt_4.id = "def456"
    cmt_4.reply = MagicMock()

    return [cmt_1, cmt_2, cmt_3, cmt_4]


@pytest.fixture
def red(stt, cmt):
    """ Fixture of mock Reddit instance """

    red = sentinel.Reddit

    red.get = MagicMock(return_value=stt)  # For most tests GET requests to Reddit will return non-error stats info
    red.subreddit = MagicMock()
    red.subreddit.return_value.comments = MagicMock(return_value=cmt)  # Testing on the fixture comments above

    red.redditor = MagicMock()  # For specifying reddit.redditor.id method side effect (or lack thereof) later

    return sentinel.Reddit


@mock.patch("bot.requests.get")
@mock.patch("bot.add_comment")
def test_bot_integration(add_comment_mock, requests_get_mock, red, cmt):
    """ Tests with different conditions for our bot; asserts length of comment ID dictionary, call count of
        comment.reply method for each comment in fixture, call count of add_comment method to add to DB """

    reply_call_count = 0

    # Valid run where usernames exist, no comment IDs exist in db yet
    ids = {}
    red.redditor.return_value.id = MagicMock()
    res = Response()
    res._content = b'{"status": 200, "error": null, "response": [{"COUNT(*)": 0}]}'
    requests_get_mock.return_value = res

    run_bot(red, ids)
    reply_call_count += 1
    assertions_if_replied(cmt, add_comment_mock, ids, reply_call_count)

    # Valid run where usernames exist, comment IDs exist in db but not in dict
    ids.clear()
    res._content = b'{"status": 200, "error": null, "response": [{"COUNT(*)": 1}]}'

    run_bot(red, ids)

    assert len(ids) == len(cmt) - 1
    for i in range(len(cmt)-1):
        assert cmt[i].reply.call_count == reply_call_count
    assert not cmt[-1].reply.called

    # Invalid run where usernames exist, DB returns error on GET request
    ids.clear()
    res._content = b'{"status": 500, "error": "some error", "response": null}'

    run_bot(red, ids)

    assert not ids
    for i in range(len(cmt) - 1):
        assert cmt[i].reply.call_count == reply_call_count
    assert not cmt[-1].reply.called

    # Invalid run where usernames don't exist, comments don't exist in DB yet
    ids.clear()
    res._content = b'{"status": 200, "error": null, "response": [{"COUNT(*)": 0}]}'
    id_exception = Response()
    id_exception._content = b'{"status": 404, "error": "user does not exist", "response": "user does not exist"}'
    red.redditor.return_value.id.side_effect = prawcore.exceptions.NotFound(id_exception)

    run_bot(red, ids)
    reply_call_count += 1
    assertions_if_replied(cmt, add_comment_mock, ids, reply_call_count)

    # Invalid run where GET call to Reddit API to get info on an activity raises some exception
    ids.clear()
    red.redditor.return_value.id = MagicMock()
    get_exception = Response()
    get_exception._content = b'{"status": 404, "error": "user stats are private", "response": "user stats are private"}'
    red.get.side_effect = prawcore.exceptions.Forbidden(get_exception)

    run_bot(red, ids)
    reply_call_count += 1
    assertions_if_replied(cmt, add_comment_mock, ids, reply_call_count)


def assertions_if_replied(cmt, add_comment_mock, ids, reply_call_count):
    assert len(ids) == len(cmt) - 1  # 1 comment won't summon
    assert add_comment_mock.call_count == (len(cmt) - 1) * reply_call_count
    for i in range(len(cmt) - 1):
        assert cmt[i].reply.call_count == reply_call_count
    assert not cmt[-1].reply.called
