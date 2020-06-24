class Statics:
    BOT_KW = "!activitystatsbot "
    UPVOTES_KW = "upvotes"
    COMMENTS_KW = "comments"
    SUBMISSIONS_KW = "submissions"
    SUBREDDIT_KW = "subreddit"
    AWARD_COUNT_KW = "awardcount"
    AWARD_FREQ_KW = "awardfreq"
    ERROR_KW = "Whoops"

    # Ensure good user request e.g. "upvotes award_count" not allowed
    CORRESPOND_MODE = {UPVOTES_KW: {SUBREDDIT_KW: None},
                       COMMENTS_KW: {SUBREDDIT_KW: None, AWARD_COUNT_KW: None, AWARD_FREQ_KW: None},
                       SUBMISSIONS_KW: {SUBREDDIT_KW: None, AWARD_COUNT_KW: None, AWARD_FREQ_KW: None}}

    FORMAT_ERROR = "Whoops - that's the incorrect comment format! Please do: '!activitystatsbot username [('upvotes' " \
                   "'subreddit') | (('comments'|'submissions') ('awardcount'|'awardfreq'|'subreddit'))]' "
    USERNAME_ERROR = "Whoops - this user doesn't appear to exist!"

    COMMENT_WORD_NO = 4
    STATS_LIMIT = 5
