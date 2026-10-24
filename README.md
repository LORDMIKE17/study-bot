# StudyBot

A Discord bot that helps my study group revise and keep on top of homework.

## Why I built it

[One or two sentences: e.g. my friends and I kept forgetting homework deadlines,
and we wanted a quick way to quiz each other before mocks.]

## What it does

- `/quiz <topic>`: multiple-choice questions with buttons for biology, chemistry, physics and maths
- `/homework add`, `/homework list`, `/homework done`: a shared homework tracker
- Automatic reminders the evening before homework is due
- `/leaderboard`: points for correct quiz answers

[Add a screenshot of the bot in action here]

## How it works

- Written in Python using the discord.py library
- Data is stored in a SQLite database, so it survives restarts
- A background loop checks every hour for homework due tomorrow
- Questions are stored in questions.json so anyone can add more

## What users said and what I changed

[e.g. "5 friends used it for 2 weeks. They said the dates were confusing,
so I added a clearer error message and example date."]

## What I learned

[2-3 points: e.g. how databases work, how to stop SQL injection,
how async code lets a program do several things at once.]

## What I'd add next

[e.g. a /addquestion command, or asking questions people got wrong more often.]

## How to run it

1. Install Python 3 and run `pip3 install -r requirements.txt`
2. Create a bot at discord.com/developers and copy its token
3. Create a `.env` file with DISCORD_TOKEN, GUILD_ID and REMINDER_CHANNEL_ID
4. Run `python3 bot.py`