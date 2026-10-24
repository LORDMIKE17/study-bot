# language.py is the little translator that helps StudyBot understand normal human sentences.
# We keep it separate from bot.py so it is easy to test without any Discord fuss.

import re
from datetime import date, timedelta

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

# These are the short, friendly names people often use when they mean a quiz topic.
TOPIC_ALIASES = {
    "bio": "biology",
    "chem": "chemistry",
    "phys": "physics",
    "math": "maths",
    "mathematics": "maths",
}


def parse_due_date(text, today=None):
    """Turn friendly phrases like 'tomorrow', 'friday', 'in 3 days', '5 nov', '05/11', and '2026-11-05'
    into a real date. If it gets confused, it kindly gives us None."""
    today = today or date.today()
    text = text.lower().strip().rstrip(".!?")
    text = re.sub(r"^(on|by|this|next)\s+", "", text)

    if text in ("today", "tonight"):
        return today
    if text == "tomorrow":
        return today + timedelta(days=1)

    # "in 3 days" is a very common little reminder phrase.
    match = re.fullmatch(r"in (\d+) days?", text)
    if match:
        return today + timedelta(days=int(match.group(1)))

    # A weekday like "friday" or "fri" means "the next time that day shows up."
    for i, day in enumerate(WEEKDAYS):
        if text in (day, day[:3]):
            days_ahead = (i - today.weekday()) % 7 or 7
            return today + timedelta(days=days_ahead)

    try:
        # "2026-11-05"
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            return date.fromisoformat(text)

        # "05/11" or "05/11/2026" (the UK style, day first, and then month)
        match = re.fullmatch(r"(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?", text)
        if match:
            day, month, year = match.groups()
            return _make_date(int(day), int(month), year, today)

        # "5 nov", "5th November", or "nov 5"
        match = (re.fullmatch(r"(\d{1,2})(?:st|nd|rd|th)?\s+([a-z]+)", text)
                 or re.fullmatch(r"([a-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?", text))
        if match:
            first, second = match.groups()
            day, month_word = (first, second) if first.isdigit() else (second, first)
            if month_word[:3] in MONTHS:
                return _make_date(int(day), MONTHS.index(month_word[:3]) + 1, None, today)
    except ValueError:  # like when someone asks for 31 February, which is a bit of a nonsense date
        return None

    return None


def _make_date(day, month, year, today):
    """Build a date and, if no year was given, make sure it lands on the next correct time it appears."""
    if year:
        year = int(year)
        if year < 100:
            year += 2000
        return date(year, month, day)
    result = date(today.year, month, day)
    if result < today:
        result = date(today.year + 1, month, day)
    return result


def find_topic(text, topics):
    """Look for a quiz topic in a sentence, like turning 'chem' into 'chemistry' for us."""
    for word in re.findall(r"[a-z]+", text.lower()):
        if word in topics:
            return word
        if TOPIC_ALIASES.get(word) in topics:
            return TOPIC_ALIASES[word]
    return None


def understand(text, topics):
    """Figure out what somebody wants from a normal sentence.
    It returns something like ("quiz", {"topic": "biology"}) so the bot knows what to do next."""
    lower = text.lower().strip()

    # Leaderboard time: "who's winning?", "show the scores"
    if re.search(r"\b(leaderboard|scores?|points|winning|top)\b", lower):
        return "leaderboard", {}

    # Finished homework: "done 3", "I've finished #2"
    match = re.search(r"\b(done|finished|completed|remove|delete)\b\D*(\d+)", lower)
    if match:
        return "homework_done", {"number": int(match.group(2))}

    # Adding homework: "add chemistry revise bonding due friday"
    if re.search(r"\b(add|set|remind)\b", lower):
        match = re.search(
            r"\b(?:add|set|remind(?:\s+(?:us|me))?(?:\s+about)?)\s+(.+?)\s+due\s+(.+)$",
            text, re.IGNORECASE)
        if not match:
            return "homework_add_help", {}
        words, when = match.group(1), match.group(2)
        words = re.sub(r"^(?:the\s+|some\s+)?(?:homework|hw)\s+(?:for\s+)?", "", words,
                       flags=re.IGNORECASE)
        parts = words.split(maxsplit=1)
        subject = parts[0].strip(":-,").capitalize()
        task = parts[1].strip(" :-,") if len(parts) > 1 else "homework"
        task = re.sub(r"^(?:homework|hw)[\s:,-]*", "", task, flags=re.IGNORECASE) or "homework"
        due = parse_due_date(when)
        if due is None:
            return "homework_bad_date", {"when": when}
        return "homework_add", {"subject": subject, "task": task, "due": due}

    # Quiz time: "quiz me on chem", "ask me a biology question"
    if re.search(r"\b(quiz|question|test me|ask me|revise)\b", lower):
        return "quiz", {"topic": find_topic(lower, topics)}

    # Homework list: "what homework is due?", "any deadlines?"
    if re.search(r"\b(homework|hw|due|deadlines?)\b", lower):
        return "homework_list", {}

    if re.search(r"\b(hi|hello|hey|yo|sup)\b", lower):
        return "hello", {}
    if re.search(r"\b(thanks|thank you|cheers|ty)\b", lower):
        return "thanks", {}

    return "help", {}