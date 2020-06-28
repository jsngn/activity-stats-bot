# Description
API to provide access to DB used by bot to determine if it has replied to certain comments.

Schema (relational) has single table to store IDs of all comments which bot has replied to. Hosted on localhost but you can run the sql script on a server.

## API
Provides access to above table. Run with `npm install` then `nodemon api.js [<env>]`. Must run before executing bot.py.

If env is not specified, localhost (`env=local`) will be used.

## Building on top of API/DB
You can add tables to the existing database schema and/or add columns to `comments` table if you want to store more data then provide more API methods for fancier processing!
