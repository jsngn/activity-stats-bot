# Description
Database used by bot to determine if it has replied to certain comments, and API to provide access to said database.

Schema (relational) has single table to store IDs of all comments which bot has replied to. Hosted on localhost but you can run the sql script on any database server.

API provides CRUD access to above table.

## Instructions
1. Edit config.js to specify the host (e.g. 'localhost'), username & password of account with CRUD privileges to your database (make a separate account on your server, don't use root as it has more privileges than necessary), default schema for API (should just be 'activity_stats_bot' unless you changed the sql script), and port on which API runs.

2. Start MySQL server (on localhost or otherwise) if not already running.

3. Run with `npm install` (first time running only) then `nodemon api.js [<env>]`. Must run before executing bot.py. If env is not specified, localhost (`env=local`) will be used.

## Building on top of API/DB
You can absolutely add tables to the existing database schema and/or add columns to `comments` table if you want to store more data then provide more API methods for fancier processing!
