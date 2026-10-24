# StudyBot

A Discord bot that helps my study group revise and keep on top of homework. You can talk to it in normal sentences, so there are no commands to remember.

## Why I built it

Fellow students kept forgetting deadlines and we needed a quicker and more interactive way to get quizzed and reminded of tests before our upcoming mock exams


## What it does

Just @mention the bot and ask:

| You type | StudyBot does |
| --- | --- |
| `@StudyBot quiz me on chem` | Asks a multiple-choice question with answer buttons |
| `@StudyBot give me a question` | Picks a random topic and asks a question |
| `@StudyBot add maths page 45 due friday` | Saves the homework with its due date |
| `@StudyBot what homework is due?` | Lists homework, soonest first, with numbers |
| `@StudyBot done 2` | Removes homework number 2 |
| `@StudyBot who's winning?` | Shows the quiz leaderboard |

- **Quizzes** in biology, chemistry, physics and maths. A correct answer earns 1 point.
- **Shared homework tracker** for the whole server.
- **Automatic reminders** posted in `#reminders` the evening before homework is due.
- **Understands everyday dates** like "tomorrow", "friday", "next mon", "in 3 days", "5 nov" and "05/11".
- **Slash commands still work** too: `/quiz`, `/homework add`, `/homework list`, `/homework done`, `/leaderboard`.
- You can also send the bot a direct message without the @.

[Add a screenshot of the bot in action here]

## How to use it on Discord

1. **Join the server.** Ask me for an invite link to the study server. StudyBot shows in the member list with an **APP** tag. If it's green, it's online.
2. **Mention the bot.** In any channel, type `@` and pick **StudyBot** from the pop-up list. Choose the one with the bot's picture and the APP tag, not the role with the same name. It should turn into a blue highlighted name.
3. **Type your message after it** in normal words, e.g. `@StudyBot quiz me on biology`, and press Enter.
4. **Answer quizzes with the buttons.** Click one of the four answers under the question. Only the person who asked can answer their own question, and the buttons stop working after 60 seconds.
5. **Add homework** by saying the subject, the task, then "due" and when: `@StudyBot add chemistry revise bonding due friday`. Everyone in the server sees the same homework list.
6. **Tick homework off.** Ask `@StudyBot what homework is due?` to see each item's number, then say `@StudyBot done 3` when number 3 is finished.
7. **Get reminders automatically.** From 5pm the evening before something is due, the bot posts a reminder in `#reminders`. Nothing to set up.
8. **Not sure what to say?** `@StudyBot help`, or just `@StudyBot`, lists what it can do.

**Prefer commands?** Type `/` in the message box to see `/quiz`, `/homework add`, `/homework list`, `/homework done` and `/leaderboard`.

**Private use:** you can also send StudyBot a direct message. Click its name, choose **Message**, and type without the @.

**Bot not replying?** It only works while it's running on my laptop. If it shows as offline (grey), it's switched off for now.

## How it works

| File | What it does |
| --- | --- |
| `bot.py` | Connects to Discord, handles messages and slash commands, runs the reminder timer |
| `language.py` | Works out what a normal sentence means (the "intent") and turns words like "friday" into real dates |
| `questions.json` | The question bank, so anyone can add questions without touching the code |
| `study.db` | A SQLite database, created automatically, that stores homework and points so nothing is lost when the bot restarts |

- Written in Python using the discord.py library.
- The language understanding is **rule-based**: it looks for key words and patterns using regular expressions. It's fast and free, but only understands phrasings it was written for.
- `language.py` is kept separate from the Discord code, so the same "brain" could be reused on another platform, like Telegram.
- Database queries use `?` placeholders to prevent SQL injection.

## What users said and what I changed

[ "5 friends used it. Typing slash commands felt annoying,
so I added natural language: now you just @ the bot and ask normally."]

## What I learned

[ how databases work, how async code lets a program
do several things at once, how to turn messy human sentences into something a program understands.]

## What I'd add next

[ a Telegram version reusing language.py, letting friends add their own questions,
or asking people the questions they got wrong more often.]

## How to run it (macOS)

1. Install Python 3 from python.org, then run **Install Certificates.command** from the Python folder in Applications.
2. Install the libraries:
   ```bash
   pip3 install -r requirements.txt
   ```
3. Create a bot at discord.com/developers, copy its token, and invite it to your server.
4. Create a `.env` file in this folder:
   ```
   DISCORD_TOKEN=your-bot-token
   GUILD_ID=your-server-id
   REMINDER_CHANNEL_ID=your-reminders-channel-id
   ```
5. Run it:
   ```bash
   python3 bot.py
   ```

The `.env` file holds the bot's secret token and is never uploaded (it's listed in `.gitignore`).
