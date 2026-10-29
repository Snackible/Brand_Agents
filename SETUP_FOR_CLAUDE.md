# Setup instructions for Claude

You are reading this because a person asked you to set up the Snackible marketing agents. Assume the person is **not technical**. Do every step yourself where you can, explain what you are doing in one plain sentence before each step, never show them commands to run, and ask them only for things that need a human: a click, a sign-in, a decision. Do one step at a time and say when each is done.

What you are setting up: two Claude skills, `competitor-research` (a weekly report on competitors) and `snackible-brand-health` (a daily report on Snackible's own listings). Each one collects data, writes a report, makes a Google Doc and emails it to the people the person names. Details are in `README.md`; you do not need to read it first.

## Rules that always apply

- **Never type passwords, one-time codes or CAPTCHAs.** If something needs a sign-in, tell the person exactly what to click, wait, then continue.
- **Ask once before installing anything.** List what you will install in plain words ("two small helper programs the agents use to read websites, about 150 MB"), get a yes, then do all the installs without asking again.
- **Do not email anyone, share any document or create any schedule until the person has said yes** to the plain-language summary the agent shows them on its first run (that is built into the skills).
- If a step fails, say what failed in one sentence, try the obvious fix once, and if it still fails, tell the person what you need from them. Do not paste error logs at them.

## Step 1: Get the files

1. Ask where to keep them, and suggest a normal folder such as `Documents/Snackible-Agents`. The folder must stay on this computer between runs, because the agents save their history in it.
2. Download the repository `https://github.com/Snackible/Brand_Agents` into that folder, using `git clone`, the GitHub CLI, or the ZIP link, whichever works on this computer.
3. The repository is private. If the download is refused, do not try to log in for the person. Tell them: "Please open the GitHub page in your browser, sign in, click the green Code button, then Download ZIP, and tell me where it saved." If they cannot see the page, they need an admin of the Snackible GitHub organisation to add them. Then unzip it into the folder yourself.

## Step 2: Install what the agents need

1. Check that Python 3.10 or newer is available. If it is not, tell the person to install it from python.org (it is a normal installer), then continue.
2. After the person's yes (see the rules above), run `pip install -r requirements.txt` inside the folder, then `python -m playwright install chromium`.
3. Run `python skills/competitor-research/scripts/preflight.py --config skills/competitor-research/config.md --data data/competitor`. Fix every `[FIX]` line it prints, then run it again until it says `ready`.

## Step 3: Install the two skills

Pick the case that matches the Claude you are running in.

- **Claude Code or Claude Desktop with file access:** copy the folders `skills/competitor-research` and `skills/snackible-brand-health` into the personal skills folder (`.claude/skills/` in the person's home folder), keeping the folder names. Then check that both skills now appear in your skill list; if they do not, restart or tell the person to reopen the app.
- **Claude in a browser, or no file access:** tell the person: "Open the folder `dist` inside the downloaded folder. Open each of the two files ending in `.skill` in Claude and click **Save skill**." (Or upload them in Claude's skills settings.) Wait for them to confirm.

## Step 4: Check the connections

Look at your own tool list and check for these three. For each one that is missing, tell the person in one sentence what it is for and what to click.

| Needed | What it is for | If missing, tell the person |
|---|---|---|
| Google Drive | saving the settings, creating and sharing the report Doc | "Please turn on the Google Drive connection in Claude's connector settings and click Allow." |
| Gmail | emailing the report | "Please turn on the Gmail connection the same way." |
| Claude in Chrome | reading Blinkit, Zepto and Instamart prices | "Please install the Claude in Chrome extension in Chrome and connect it to this Claude. Keep Chrome open when reports run." |

The agents still work without Claude in Chrome, but the quick-commerce prices will be missing and the report will say so. Drive and Gmail are needed for the email.

## Step 5: Run the first report

Tell the person: "Now I'll make the first report. It takes about five to ten minutes. I'll ask you a few questions at the start, once only."

1. Start with the daily one: use the `snackible-brand-health` skill (ask it to "Run the daily brand health report"). Then the weekly one: use the `competitor-research` skill ("Run the weekly competitor report").
2. On the first run each skill asks the person who should receive the report, whether to send automatically, and when to run. Relay those questions in plain words, one message, and pass their answers back. The skill creates the schedule only after the person says yes.
3. The first report is a **baseline**: it shows the current picture and no changes yet. Tell the person this, so they are not surprised. Changes show from the second run.

## Step 6: Tell the person what happens next

Say, in plain words: the reports will arrive by email at the times they chose; the computer has to be on and the Claude app open at those times (a missed report arrives when the app next opens); the first two weeks are worth comparing against what the team already knows; and they can say "change report recipients" or "change the report schedule" at any time.

If the person wants to understand more, `docs/Setup_Guide_Adding_the_Agents_to_a_New_Claude.pdf` is a short guide written for them.

## If the person says something is not working

Run the preflight check (step 2.3) again, read what it says, fix it, and explain what was wrong in one sentence. The usual causes are: the computer or Chrome was closed at the scheduled time, a connection (Drive, Gmail, Chrome) was turned off, or the downloaded folder was moved or deleted.
