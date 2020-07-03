""" Testing for extractor.py (Extractor class)
    Josephine Nguyen, 2020 """

import pytest
from unittest.mock import sentinel
from urllib.parse import urlparse

import praw
import pyconfig
from extractor import Extractor
from statics import Statics


@pytest.fixture
def red():
    """ Fixture of valid praw.Reddit instance """

    return praw.Reddit(username=pyconfig.username, password=pyconfig.password, client_id=pyconfig.client_id,
                       client_secret=pyconfig.client_secret, user_agent="Activity stats comment bot by /u/swinii")


@pytest.fixture
def usr():
    """ Fixture of string for username to get stats of """

    return "swinii"  # FOR SMOOTHEST TEST DEMO REPLACE WITH PUBLIC UPVOTES AND AWARDS ON SUBMISSIONS


@pytest.fixture
def ext(red, usr):
    """ Fixture of a valid Extractor instance, makes use of valid praw.Reddit fixture """

    reddit = red
    username = usr
    return Extractor(reddit, username)


def test_extractor_constructor(ext, usr):
    """ Test attributes of extractor """

    assert type(ext.reddit) is praw.Reddit
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


def test_get_calls(ext):
    """ Test that all GET calls succeed and return a praw Listing object, not NoneType """

    assert type(ext.get_upvotes_stats()) is praw.reddit.models.Listing
    assert type(ext.get_submissions_stats()) is praw.reddit.models.Listing
    assert type(ext.get_comments_stats()) is praw.reddit.models.Listing


def test_get_from_list(ext):
    """ Call function to test type of dictionary response and its key-value pair types, also tests that only 1 of the
        functions return URL as keys """

    res = ext.get_subreddit_count_from_list(ext.get_upvotes_stats())
    check_get_from_list_content(res)
    for url in res:
        assert urlparse(url).netloc == ""  # not URL

    res = ext.get_award_freqs_from_list(ext.get_submissions_stats())
    check_get_from_list_content(res)
    for url in res:
        assert urlparse(url).netloc == ""

    res = ext.get_award_count_from_list(ext.get_submissions_stats())
    check_get_from_list_content(res)
    for url in res:
        assert urlparse(url).netloc != ""  # is URL


def check_get_from_list_content(res):
    """ Test that each get_x_from_list() return value is right type, including keys and values """

    assert type(res) is dict
    if res.keys():
        assert set(map(type, res.keys())) == {str}
    if res.values():
        assert set(map(type, res.values())) == {int}


def test_extract(ext):
    """ Test valid runs of extract() """

    check_extract_content(ext, Statics.UPVOTES_KW, Statics.SUBREDDIT_KW)
    check_extract_content(ext, Statics.COMMENTS_KW, Statics.SUBREDDIT_KW)
    check_extract_content(ext, Statics.COMMENTS_KW, Statics.AWARD_FREQ_KW)
    check_extract_content(ext, Statics.COMMENTS_KW, Statics.AWARD_COUNT_KW)
    check_extract_content(ext, Statics.SUBMISSIONS_KW, Statics.SUBREDDIT_KW)
    check_extract_content(ext, Statics.SUBMISSIONS_KW, Statics.AWARD_FREQ_KW)
    check_extract_content(ext, Statics.SUBMISSIONS_KW, Statics.AWARD_COUNT_KW)


def check_extract_content(ext, activity, mode):
    """ Make sure no error returned for a valid extract() call (NOT including the format checking that should've
        occurred in bot.py) and correct result for activity & mode types are returned """

    res = ext.extract(activity, mode)
    assert type(res) is dict  # Make sure something is returned (not NoneType) and it's a dict
    assert Statics.EXCEPTION_KW not in res
    assert activity + "_" + mode in res


def test_extract_exception(ext):
    """ Test that an exception is raised, and that result dictionary indicates error """

    ext.reddit = sentinel.Reddit  # Not actual praw.Reddit instance, will throw some exception
    with pytest.raises(Exception):
        res = ext.extract(Statics.COMMENTS_KW, Statics.AWARD_COUNT_KW)
        assert type(res) is dict  # Make sure something is returned (not NoneType) and it's a dict
        assert Statics.EXCEPTION_KW in res
        assert Statics.COMMENTS_KW + "_" + Statics.AWARD_COUNT_KW in res
