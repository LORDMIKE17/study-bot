# StudyBot: a Discord bot for quizzes, homework tracking and reminders.
# Talk to it by @mentioning it ("@StudyBot quiz me on chemistry"),
# or use the slash commands (/quiz, /homework, /leaderboard).
# Run with: python3 bot.py

import os
import re
import json
import random
import sqlite3
from datetime import date, datetime, timedelta

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

from language import understand, parse_due_date

# ---------- Setup ----------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = discord.Object(id=int(os.getenv("GUILD_ID")))
REMINDER_CHANNEL_ID = int(os.getenv("REMINDER_CHANNEL_ID"))

client = discord.Client(intents=discord.Intents.default())
tree = app_commands.CommandTree(client)
NO_PINGS = discord.AllowedMentions.none()

HELP_TEXT = (
    "Just @ me and ask normally! For example:\n"
    "- **quiz me on chemistry** (or biology, physics, maths)\n"
    "- **what homework is due?**\n"
    "- **add maths page 45 due friday**\n"
    "- **done 2** (when homework number 2 is finished)\n"
    "- **who's winning?**"
)

# ---------- Database ----------
db = sqlite3.connect("study.db")
db.execute("""CREATE TABLE IF NOT EXISTS homework (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT, task TEXT, due_date TEXT,
    added_by INTEGER, reminded INTEGER DEFAULT 0)""")
db.execute("""CREATE TABLE IF NOT EXISTS points (
    user_id INTEGER PRIMARY KEY, score INTEGER DEFAULT 0)""")
db.commit()


def add_point(user_id):
    db.execute(
        "INSERT INTO points (user_id, score) VALUES (?, 1) "
        "ON CONFLICT(user_id) DO UPDATE SET score = score + 1",
        (user_id,),
    )
    db.commit()


def save_homework(subject, task, due_date, user_id):
    db.execute(
        "INSERT INTO homework (subject, task, due_date, added_by) VALUES (?, ?, ?, ?)",
        (subject, task, due_date.isoformat(), user_id))
    db.commit()
    return f"📚 Added **{subject}**: {task} (due {due_date:%a %d %b})"


def homework_list_text():
    rows = db.execute(
        "SELECT id, subject, task, due_date FROM homework "
        "WHERE due_date >= ? ORDER BY due_date",
        (date.today().isoformat(),)).fetchall()
    if not rows:
        return "No homework due. 🎉"
    lines = []
    for hw_id, subject, task, due in rows:
        due_date = date.fromisoformat(due)
        lines.append(f"`#{hw_id}` **{subject}**: {task} (due {due_date:%a %d %b})")
    return "\n".join(lines)


def remove_homework(number):
    cur = db.execute("DELETE FROM homework WHERE id = ?", (number,))
    db.commit()
    if cur.rowcount:
        return f"✅ Removed #{number}. Nice work!"
    return f"I couldn't find homework #{number}. Ask me **what homework is due?** to see the numbers."


def leaderboard_text():
    rows = db.execute(
        "SELECT user_id, score FROM points ORDER BY score DESC LIMIT 10").fetchall()
    if not rows:
        return "No points yet. Ask me to quiz you!"
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, (user_id, score) in enumerate(rows):
        badge = medals[i] if i < 3 else f"{i + 1}."
        lines.append(f"{badge} <@{user_id}>: {score} pts")
    return "\n".join(lines)


# ---------- Quiz ----------
with open("questions.json", encoding="utf-8") as f:
    QUESTIONS = json.load(f)


class QuizView(discord.ui.View):
    def __init__(self, question, user_id):
        super().__init__(timeout=60)
        self.question = question
        self.user_id = user_id
        for i, option in enumerate(question["options"]):
            button = discord.ui.Button(label=option, style=discord.ButtonStyle.primary)
            button.callback = self.make_callback(i)
            self.add_item(button)

    def make_callback(self, index):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message(
                    "That's not your question! Ask me for your own quiz.", ephemeral=True)
                return
            correct = self.question["answer"]
            for item in self.children:
                item.disabled = True
            if index == correct:
                add_point(interaction.user.id)
                result = "✅ Correct! +1 point"
            else:
                result = f"❌ Not quite. The answer was **{self.question['options'][correct]}**"
            await interaction.response.edit_message(
                content=f"{self.question['q']}\n\n{result}", view=self)
            self.stop()
        return callback


def pick_question(topic):
    """Pick a random question. With no topic, pick a random topic too."""
    topic = topic or random.choice(list(QUESTIONS))
    return topic, random.choice(QUESTIONS[topic])


# ---------- Talking normally (@mentions and DMs) ----------
@client.event
async def on_message(message):
    if message.author.bot:
        return
    is_dm = isinstance(message.channel, discord.DMChannel)
    if client.user not in message.mentions and not is_dm:
        return  # only answer when someone @mentions the bot, or in a DM

    text = re.sub(r"<@!?\d+>", "", message.content).strip()  # remove the @StudyBot part
    intent, details = understand(text, list(QUESTIONS))

    if intent == "quiz":
        topic, question = pick_question(details["topic"])
        await message.reply(f"**{topic.capitalize()}:** {question['q']}",
                            view=QuizView(question, message.author.id), mention_author=False)
        return

    if intent == "homework_add":
        reply = save_homework(details["subject"], details["task"], details["due"],
                              message.author.id)
    elif intent == "homework_bad_date":
        reply = (f"I didn't understand the date \"{details['when']}\". "
                 "Try something like **friday**, **tomorrow**, **5 nov** or **in 3 days**.")
    elif intent == "homework_add_help":
        reply = "When's it due? Try: **add chemistry revise bonding due friday**"
    elif intent == "homework_list":
        reply = homework_list_text()
    elif intent == "homework_done":
        reply = remove_homework(details["number"])
    elif intent == "leaderboard":
        reply = leaderboard_text()
    elif intent == "hello":
        reply = f"Hey {message.author.display_name}! Want a quiz? Just say **quiz me on biology**."
    elif intent == "thanks":
        reply = "Any time! Good luck with the revision 💪"
    else:
        reply = HELP_TEXT

    await message.reply(reply, allowed_mentions=NO_PINGS)


# ---------- Slash commands (still work too) ----------
@tree.command(name="hello", description="Say hi to the bot")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hi! Ready to revise? 📚\n\n" + HELP_TEXT)


@tree.command(name="quiz", description="Get a quiz question")
@app_commands.describe(topic="biology, chemistry, physics or maths")
async def quiz(interaction: discord.Interaction, topic: str):
    topic = topic.lower().strip()
    if topic not in QUESTIONS:
        await interaction.response.send_message(
            "I don't have that topic. Try: " + ", ".join(QUESTIONS), ephemeral=True)
        return
    topic, question = pick_question(topic)
    await interaction.response.send_message(
        question["q"], view=QuizView(question, interaction.user.id))


homework = app_commands.Group(name="homework", description="Track homework")


@homework.command(name="add", description="Add a piece of homework")
@app_commands.describe(subject="e.g. Chemistry", task="What needs doing",
                       due="When it's due, e.g. friday, tomorrow or 5 nov")
async def homework_add(interaction: discord.Interaction, subject: str, task: str, due: str):
    due_date = parse_due_date(due)
    if due_date is None:
        await interaction.response.send_message(
            "I didn't understand that date. Try **friday**, **tomorrow** or **5 nov**.",
            ephemeral=True)
        return
    await interaction.response.send_message(
        save_homework(subject, task, due_date, interaction.user.id))


@homework.command(name="list", description="Show upcoming homework")
async def homework_list(interaction: discord.Interaction):
    await interaction.response.send_message(homework_list_text())


@homework.command(name="done", description="Remove homework by its number")
@app_commands.describe(number="The # number shown in /homework list")
async def homework_done(interaction: discord.Interaction, number: int):
    await interaction.response.send_message(remove_homework(number))


tree.add_command(homework)


@tree.command(name="leaderboard", description="See the top quiz scorers")
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.send_message(leaderboard_text(), allowed_mentions=NO_PINGS)


# ---------- Reminders ----------
@tasks.loop(hours=1)
async def reminder_loop():
    if datetime.now().hour < 17:  # only remind from 5pm onwards
        return
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    rows = db.execute(
        "SELECT id, subject, task FROM homework WHERE due_date = ? AND reminded = 0",
        (tomorrow,)).fetchall()
    if not rows:
        return
    channel = client.get_channel(REMINDER_CHANNEL_ID)
    for hw_id, subject, task in rows:
        await channel.send(f"⏰ Reminder: **{subject}**: {task} is due tomorrow!")
        db.execute("UPDATE homework SET reminded = 1 WHERE id = ?", (hw_id,))
    db.commit()


# ---------- Start up ----------
@client.event
async def on_ready():
    tree.copy_global_to(guild=GUILD)
    await tree.sync(guild=GUILD)
    if not reminder_loop.is_running():
        reminder_loop.start()
    print(f"Logged in as {client.user}")


client.run(TOKEN)