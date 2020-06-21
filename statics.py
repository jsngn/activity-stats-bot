class Statics:
    BOT_KW = "!activitystatsbot "
    UPVOTES_KW = "upvotes"
    COMMENTS_KW = "comments"
    SUBMISSIONS_KW = "submissions"
    SUBREDDIT_KW = "subreddit"
    AWARD_COUNT_KW = "award_count"
    AWARD_FREQ_KW = "award_freq"
    ERROR_KW = "Whoops"

    FORMAT_ERROR = "Whoops - that's the incorrect comment format! Please do: '!activitystatsbot username [('upvotes' " \
                   "'subreddit') | (('comments'|'submissions') ('award_count'|'award_freq'|'subreddit'))]' "
    USERNAME_ERROR = "Whoops - this user doesn't appear to exist!"
    ACTIVITY_ERROR = "Whoops - after username, please specify 'upvotes', 'comments', or 'submissions' then whether " \
                     "you want to view 'award_count', 'award_freq', or 'subreddit' stats! See docs for more."

    COMMENT_WORD_NO = 4
    STATS_LIMIT = 5
