""" Unit testing for bot.py -- run_bot() not included as it's essentially driver code
    Josephine Nguyen, 2020 """

from unittest import mock
from unittest.mock import sentinel, MagicMock

from bot import *
from requests.models import Response


@mock.patch("bot.requests.get")
def test_has_replied(requests_get_mock):
    """ Test that correct value is returned for erroneous and valid API responses """

    # Erroneous response from API, reflected in status
    res = Response()
    res._content = b'{"status": 500, "error": "some error", "response": null}'
    requests_get_mock.return_value = res
    assert has_replied("123abc") == 2

    # Erroneous response from API, reflected in response message
    res = Response()
    res._content = b'{"status": 200, "error": null, "response": null}'
    requests_get_mock.return_value = res
    assert has_replied("123abc") == 2

    # Comment ID exists in db
    res = Response()
    res._content = b'{"status": 200, "error": null, "response": [{"COUNT(*)": 1}]}'
    requests_get_mock.return_value = res
    assert has_replied("123abc") == 1

    # Comment ID doesn't exist in db
    res = Response()
    res._content = b'{"status": 200, "error": null, "response": [{"COUNT(*)": 0}]}'
    requests_get_mock.return_value = res
    assert has_replied("123abc") == 0

    assert requests_get_mock.call_count == 4


@mock.patch("bot.requests")
def test_add_comment(requests_mock):
    """ Test that POST request is made; no further testing since if POST request is made, there's no difference in
        any return values/exceptions/etc. regardless of status returned by API """

    add_comment("123abc")
    assert requests_mock.post.called


def test_format_comment():
    """ Test that correct reply format is returned for each activity and mode, including ones that wouldn't pass earlier
        format checks """

    user = "swinii"
    assert format_comment(user, Statics.UPVOTES_KW, Statics.SUBREDDIT_KW) == f"{user}'s {Statics.UPVOTES_KW} most " \
                                                                             f"commonly appear in these " \
                                                                             f"subreddits:\n\n"
    # Shouldn't pass earlier format checks
    assert format_comment(user, Statics.UPVOTES_KW, Statics.AWARD_FREQ_KW) == f"{user} received these awards most " \
                                                                              f"commonly on their " \
                                                                              f"{Statics.UPVOTES_KW}:\n\n"
    # Shouldn't pass earlier format checks
    assert format_comment(user, Statics.UPVOTES_KW, Statics.AWARD_COUNT_KW) == f"{user} received most awards on " \
                                                                               f"these {Statics.UPVOTES_KW}:\n\n"

    assert format_comment(user, Statics.COMMENTS_KW, Statics.SUBREDDIT_KW) == f"{user}'s {Statics.COMMENTS_KW} most " \
                                                                              f"commonly appear in these " \
                                                                              f"subreddits:\n\n"
    assert format_comment(user, Statics.COMMENTS_KW, Statics.AWARD_FREQ_KW) == f"{user} received these awards most " \
                                                                               f"commonly on their " \
                                                                               f"{Statics.COMMENTS_KW}:\n\n"
    assert format_comment(user, Statics.COMMENTS_KW, Statics.AWARD_COUNT_KW) == f"{user} received most awards on " \
                                                                                f"these {Statics.COMMENTS_KW}:\n\n"

    assert format_comment(user, Statics.SUBMISSIONS_KW, Statics.SUBREDDIT_KW) == f"{user}'s {Statics.SUBMISSIONS_KW} " \
                                                                                 f"most commonly appear in these " \
                                                                                 f"subreddits:\n\n"
    assert format_comment(user, Statics.SUBMISSIONS_KW, Statics.AWARD_FREQ_KW) == f"{user} received these awards most " \
                                                                                  f"commonly on their " \
                                                                                  f"{Statics.SUBMISSIONS_KW}:\n\n"
    assert format_comment(user, Statics.SUBMISSIONS_KW, Statics.AWARD_COUNT_KW) == f"{user} received most awards on " \
                                                                                   f"these {Statics.SUBMISSIONS_KW}" \
                                                                                   f":\n\n"

    assert format_comment(user, "not a real activity", "not a real mode") == Statics.FORMAT_ERROR + " Results below " \
                                                                                                    "may not be " \
                                                                                                    "meaningful.\n\n"


def test_get_unit():
    """ Test that correct units are returned for each activity and mode, including ones that wouldn't pass earlier
        format checks """

    assert get_unit(Statics.UPVOTES_KW, Statics.SUBREDDIT_KW) == "upvotes"
    assert get_unit(Statics.UPVOTES_KW, Statics.AWARD_FREQ_KW) == "awards"  # Should never happen because format check
    assert get_unit(Statics.UPVOTES_KW, Statics.AWARD_COUNT_KW) == "awards"  # Should never happen because format check

    assert get_unit(Statics.COMMENTS_KW, Statics.SUBREDDIT_KW) == "comments"
    assert get_unit(Statics.COMMENTS_KW, Statics.AWARD_FREQ_KW) == "awards"
    assert get_unit(Statics.COMMENTS_KW, Statics.AWARD_COUNT_KW) == "awards"

    assert get_unit(Statics.SUBMISSIONS_KW, Statics.SUBREDDIT_KW) == "submissions"
    assert get_unit(Statics.SUBMISSIONS_KW, Statics.AWARD_FREQ_KW) == "awards"
    assert get_unit(Statics.SUBMISSIONS_KW, Statics.AWARD_COUNT_KW) == "awards"

    assert get_unit("not a real activity", "not a real mode") == ""


@mock.patch("bot.add_comment")
def test_reply_handler(add_comment_mock):
    """ Test that in a valid, no-exceptions-raised run of function, all necessary calls to "helper functions" are made
        and dictionary in params is modified correctly """

    comment = sentinel.Comment
    comment.id = "123abc"
    comment.reply = MagicMock()
    reply = "any reply"
    ids = {}

    assert reply_handler(comment, reply, ids) is None
    assert add_comment_mock.called
    assert comment.reply.called
    assert comment.id in ids


@mock.patch("bot.add_comment")
def test_reply_handler_exception(add_comment_mock):
    """ Test that in an exceptions-raised run of function, all necessary calls to "helper functions" up to where
        exception is raised are made and dictionary in params wouldn't be modified if exception raised before
        that point

        Since add_comment() doesn't raise any exceptions and dict is passed internally (so not likely TypeError),
        most likely errors will happen with reply() function of praw's Reddit comment object i.e. the case tested """

    comment = sentinel.Comment
    comment.id = "123abc"
    comment.reply = MagicMock()
    comment.reply.side_effect = Exception()
    reply = "any reply"
    ids = {}

    assert reply_handler(comment, reply, ids) is None
    assert not add_comment_mock.called
    assert comment.reply.called
    assert comment.id not in ids
