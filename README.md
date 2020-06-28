# activisualizer
Activity stats bot for Reddit

## Description
A summon-able bot that comments a user's upvote/comment/submission stats taken from their last 100 upvotes/comments/submissions.

By default, the bot only comments the stats for 5 upvotes/comments/submissions with the highest stats (see [Format explanation](https://github.com/jsngn/activity-stats-bot#format-explanation)), but you can configure this.

## Summon format
`!activitystatsbot <username> ((upvotes subreddit) | ((comments|submissions) (awardcount|awardfreq|subreddit)))`

### Format explanation
`upvotes subreddit`: 5 subreddits where most of the user's upvotes go. Reply format: `<subreddit>: <upvotes received from user>`

`(comments|submissions) subreddit`: 5 subreddits where the user comments/submits most. Reply format: `<subreddit>: <comments/submissions posted by user>`

`(comments|submissions) awardcount`: 5 comments/submissions for which the user received the most awards. Reply format: `<comment/submission>: <award count>`

`(comments|submissions) awardfreq`: 5 awards received most often by the user through their comments/submissions. Reply format: `<award name>: <number received>`

## Database connection issue
If you get a 'Too many connections' error for the MySQL connection (visible in log), try restarting the API and possibly the database.