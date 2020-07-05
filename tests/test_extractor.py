""" Testing for extractor.py (Extractor class)
    Josephine Nguyen, 2020 """

import pytest
from unittest.mock import sentinel, MagicMock
from urllib.parse import urlparse

from extractor import Extractor
from statics import Statics


@pytest.fixture
def lis():
    """ Fixture of mock Listing instance to be used as default return of GET requests; for test functions that
        don't require extracting subreddit or award count/freq """

    return sentinel.Listing


@pytest.fixture
def red(lis):
    """ Fixture of mock Reddit instance """

    red = sentinel.Reddit
    red.get = MagicMock(return_value=lis)
    return sentinel.Reddit


@pytest.fixture
def stt():
    """ Fixture of mock results w/ important info returned by GET requests; for test functions that
        require extracting subreddit or award count/freq """

    # Make 2 mock results to be returned from mock Reddit.get(); actual Listing objects would have more attributes
    res_1 = MagicMock()
    res_1.subreddit = "memes"
    res_1.permalink = "/r/memes"  # Actual link returned would point to a specific comment, not this
    res_1.all_awardings = [{"name": "Gold", "count": 7}, {"name": "Silver", "count": 17}]

    res_2 = MagicMock()
    res_2.subreddit = "redditdev"
    res_2.permalink = "/r/redditdev"
    res_2.all_awardings = [{"name": "Gold", "count": 1}, {"name": "Silver", "count": 12}]

    return [res_1, res_2]


@pytest.fixture
def usr():
    """ Fixture of string for username to get stats of """

    return "swinii"


@pytest.fixture
def ext(red, usr):
    """ Fixture of a valid Extractor instance, makes use of valid praw.Reddit fixture """

    reddit = red
    username = usr
    return Extractor(reddit, username)


def test_extractor_constructor(red, ext, usr):
    """ Test attributes of extractor """

    assert ext.reddit is red
    assert ext.username == usr
    assert type(ext.activity_action) is dict and type(ext.mode_action) is dict
    assert len(ext.activity_action) == len(ext.activity_action) == 3

    # Make sure correct functions are called by extract() later
    assert ext.activity_action[Statics.UPVOTES_KW] == ext.get_upvotes_stats
    assert ext.activity_action[Statics.COMMENTS_KW] == ext.get_comments_stats
    assert ext.activity_action[Statics.SUBMISSIONS_KW] == ext.get_submissions_stats
    assert ext.mode_action[Statics.SUBREDDIT_KW] == ext.get_subreddit_count_from_list
    assert ext.mode_action[Statics.AWARD_COUNT_KW] == ext.get_award_count_from_list
    assert ext.mode_action[Statics.AWARD_FREQ_KW] == ext.get_award_freqs_from_list


def test_get_calls(red, ext, lis):
    """ Test that all GET requests return expected value """

    assert ext.get_upvotes_stats() is lis and red.get.called
    assert ext.get_submissions_stats() is lis and red.get.called
    assert ext.get_comments_stats() is lis and red.get.called


def test_get_from_list(red, ext, stt):
    """ Call function to test type of dictionary response, its key-value pair types, and length, also tests that only
        1 of the functions return URL as keys """

    red.get.return_value = stt

    res = ext.get_subreddit_count_from_list(ext.get_upvotes_stats())
    check_get_from_list_content(res, stt)
    for url in res:
        assert urlparse(url).netloc == ""  # not URL

    res = ext.get_award_freqs_from_list(ext.get_submissions_stats())
    check_get_from_list_content(res, stt)
    for url in res:
        assert urlparse(url).netloc == ""

    res = ext.get_award_count_from_list(ext.get_submissions_stats())
    check_get_from_list_content(res, stt)
    for url in res:
        assert urlparse(url).netloc != ""  # is URL


def check_get_from_list_content(res, stt):
    """ Test that each get_x_from_list() return value is right type, including keys and values, and length """

    assert type(res) is dict
    assert len(res) == len(stt)

    if res.keys():
        assert set(map(type, res.keys())) == {str}
    if res.values():
        assert set(map(type, res.values())) == {int}


def test_extract(red, ext, stt):
    """ Test valid runs of extract() """

    red.get.return_value = stt

    check_extract_content(ext, stt, Statics.UPVOTES_KW, Statics.SUBREDDIT_KW)
    check_extract_content(ext, stt, Statics.COMMENTS_KW, Statics.SUBREDDIT_KW)
    check_extract_content(ext, stt, Statics.COMMENTS_KW, Statics.AWARD_FREQ_KW)
    check_extract_content(ext, stt, Statics.COMMENTS_KW, Statics.AWARD_COUNT_KW)
    check_extract_content(ext, stt, Statics.SUBMISSIONS_KW, Statics.SUBREDDIT_KW)
    check_extract_content(ext, stt, Statics.SUBMISSIONS_KW, Statics.AWARD_FREQ_KW)
    check_extract_content(ext, stt, Statics.SUBMISSIONS_KW, Statics.AWARD_COUNT_KW)


def check_extract_content(ext, stt, activity, mode):
    """ Make sure no error returned for a valid extract() call (NOT including the format checking that should've
        occurred in bot.py) and correct result for activity & mode types are returned """

    res = ext.extract(activity, mode)
    assert type(res) is dict  # Make sure something is returned (not NoneType) and it's a dict
    assert Statics.EXCEPTION_KW not in res
    assert activity + "_" + mode in res
    assert type(res[activity + "_" + mode]) is dict
    assert len(res[activity + "_" + mode]) == len(stt)  # All (mock) results are present


def test_extract_exception(red, ext):
    """ Test when an exception is raised, and that result dictionary indicates error, not normal result """

    red.get.side_effect = Exception()
    res = ext.extract(Statics.COMMENTS_KW, Statics.AWARD_COUNT_KW)
    assert type(res) is dict  # Make sure something is returned (not NoneType) and it's a dict
    assert Statics.EXCEPTION_KW in res
    assert Statics.COMMENTS_KW + "_" + Statics.AWARD_COUNT_KW not in res
