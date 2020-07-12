# activity-stats-bot
Activity stats bot for Reddit

![Bot Screenshot](https://imgur.com/i03NoZk)

## Description
A summon-able bot that comments a user's upvote/comment/submission stats taken from their last 100 upvotes/comments/submissions.

By default, the bot only comments the stats for 5 upvotes/comments/submissions with the highest stats (see [Format explanation](https://github.com/jsngn/activity-stats-bot#format-explanation)), but you can configure this.

## Dependencies
1. [Python 3.8](https://www.python.org/downloads/)

2. [praw](https://praw.readthedocs.io/en/latest/getting_started/installation.html)

3. [MySQL](https://dev.mysql.com/downloads/mysql/)

4. [Node.JS](https://nodejs.org/en/download/)

## Run this bot
1. Create an app [here](https://www.reddit.com/prefs/apps/) using your bot's account. Importantly, fill in name (whatever you want), type (Script), redirect uri (http://localhost:8080).

2. Edit pyconfig.py to specify your bot's account username & password, subreddit where bot will run, client ID and secret from the page where you just created your app.

3. Edit other configurations in pyconfig.py if necessary. Feel free to change it at any point later on, too.

4. Start MySQL server (on localhost or otherwise) if not already running.

5. Run create_bot_schema.sql (in ./db/) using command line or MySQL Workbench.

6. In this (root) directory: `cd db` then edit config.js (see [instructions](https://github.com/jsngn/activity-stats-bot/tree/master/db#instructions)), `npm install` (if first time running), then `nodemon api.js [<env>]` (every time you run bot).

7. Finally, run the bot: `python3 bot.py` in this (root) directory.

## Summon format
`!activitystatsbot <username> ((upvotes subreddit) | ((comments|submissions) (awardcount|awardfreq|subreddit)))`

### Format explanation
`upvotes subreddit`: 5 subreddits where most of the user's upvotes go. Reply format: `<subreddit>: <upvotes received from user>`

`(comments|submissions) subreddit`: 5 subreddits where the user comments/submits most. Reply format: `<subreddit>: <comments/submissions posted by user>`

`(comments|submissions) awardcount`: 5 comments/submissions for which the user received the most awards. Reply format: `<comment/submission>: <award count>`

`(comments|submissions) awardfreq`: 5 awards received most often by the user through their comments/submissions. Reply format: `<award name>: <number received>`

## Database connection issue
If you get a 'Too many connections' error for the MySQL connection (visible in log), try restarting the API and possibly the database.
