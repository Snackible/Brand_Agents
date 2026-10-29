"""Builds docs/Setup_Guide_Adding_the_Agents_to_a_New_Claude.pdf (needs reportlab)."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, ListFlowable, ListItem, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

OUT = Path(__file__).parent / "Setup_Guide_Adding_the_Agents_to_a_New_Claude.pdf"

INK = colors.HexColor("#1f2937")
MUTED = colors.HexColor("#6b7280")
ACCENT = colors.HexColor("#0f766e")
RULE = colors.HexColor("#d1d5db")
HEAD_BG = colors.HexColor("#f3f4f6")

base = getSampleStyleSheet()
body = ParagraphStyle("body", parent=base["Normal"], fontName="Helvetica", fontSize=9.6, leading=13.6,
                      textColor=INK, alignment=TA_LEFT, spaceAfter=5)
small = ParagraphStyle("small", parent=body, fontSize=8.6, leading=11.6, textColor=MUTED)
h1 = ParagraphStyle("h1", parent=body, fontName="Helvetica-Bold", fontSize=19, leading=23, spaceAfter=3, textColor=INK)
sub = ParagraphStyle("sub", parent=body, fontSize=10.5, leading=14, textColor=MUTED, spaceAfter=10)
h2 = ParagraphStyle("h2", parent=body, fontName="Helvetica-Bold", fontSize=12.5, leading=16, spaceBefore=12,
                    spaceAfter=5, textColor=ACCENT, keepWithNext=True)
cell = ParagraphStyle("cell", parent=body, fontSize=8.7, leading=11.4, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
code = ParagraphStyle("code", parent=body, fontName="Courier", fontSize=8.6, leading=11.6, backColor=HEAD_BG,
                      borderPadding=(4, 5, 4, 5), spaceBefore=3, spaceAfter=8, leftIndent=4)


def P(t, s=body):
    return Paragraph(t, s)


def bullets(items, style=body):
    return ListFlowable([ListItem(P(t, style), leftIndent=12) for t in items], bulletType="bullet",
                        bulletFontSize=7, leftIndent=12, bulletOffsetY=-1, spaceAfter=4)


def steps(items):
    return ListFlowable([ListItem(P(t), leftIndent=16) for t in items], bulletType="1", leftIndent=16,
                        bulletFontName="Helvetica-Bold", bulletFontSize=9.4, spaceAfter=5)


def table(rows, widths, header=True):
    data = [[P(c, cellb if (header and i == 0) else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if header else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
          ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
          ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    if header:
        st.append(("BACKGROUND", (0, 0), (-1, 0), HEAD_BG))
    t.setStyle(TableStyle(st))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(20 * mm, 11 * mm, "Snackible Marketing Agents: setup guide")
    canvas.drawRightString(A4[0] - 20 * mm, 11 * mm, f"Page {doc.page}")
    canvas.restoreState()


s = []
s += [P("Adding the Snackible Marketing Agents to a new Claude", h1),
      P("Setup guide for whoever is setting up a different Claude. Read it once, top to bottom, before the first run. "
        "The agents are installed from GitHub: <a href='https://github.com/Snackible/Brand_Agents' color='#0f766e'>"
        "https://github.com/Snackible/Brand_Agents</a>", sub)]

s += [P("1. What you are installing", h2),
      P("Two Claude skills built from the Marketing Agents build plan. Each one collects data, saves a dated snapshot, "
        "compares it with the previous snapshot, writes a report, and emails it as a Google Doc."),
      table([["Agent", "Cadence", "What it reports"],
             ["Competitor Research (skill: competitor-research)", "Weekly",
              "What changed across competitors: prices and price per 100g, Meta ads, Amazon ratings and discounts, "
              "quick-commerce prices, claims, gifting, news."],
             ["Snackible Brand Health (skill: snackible-brand-health)", "Daily",
              "Snackible's own listings (stock, price, MRP), Amazon keyword rank, ratings, mentions. "
              "Leads with what needs attention today."]],
            [58, 20, 92])]

s += [P("2. What the new Claude needs", h2),
      P("The skills travel to a new Claude. The machine and the accounts do not, so check each line below. "
        "On its first run the agent also checks this list itself and tells you what is missing."),
      table([["Need", "Why", "How to check or fix"],
             ["A Claude that can run Python 3.10 or newer", "The collectors are Python scripts.",
              "Ask Claude to run <font name='Courier'>python --version</font>. Without code execution the agents cannot collect data."],
             ["Python packages <font name='Courier'>requests</font> and <font name='Courier'>playwright</font>, "
              "plus a headless Chromium", "Amazon, Meta Ad Library, Shopify store feeds and YouTube are read with them.",
              "From inside the downloaded repository folder: <font name='Courier'>pip install -r requirements.txt</font> then "
              "<font name='Courier'>python -m playwright install chromium</font>. The agent asks before installing anything."],
             ["Claude in Chrome extension, connected, on the machine that runs the agent",
              "Blinkit, Zepto and Instamart block scripts but load in a normal browser.",
              "Install the extension in Chrome and connect it to this Claude. Keep Chrome open during runs."],
             ["Google Drive and Gmail connectors enabled", "Docs, sharing, the saved settings file and the email.",
              "Turn both on in the Claude's connector settings."],
             ["A working folder that survives between runs", "Snapshots are saved there. Changes can only be shown if "
              "yesterday's or last week's snapshot is still there.",
              "Open the folder you downloaded from GitHub as Claude's working folder. The agents create a <font name='Courier'>data</font> "
              "folder inside it (git ignores it). In a throwaway sandbox every run is a baseline."]],
            [52, 52, 66])]

s += [P("3. Install, step by step", h2),
      steps([
          "Get access to the repository: <a href='https://github.com/Snackible/Brand_Agents' color='#0f766e'>"
          "https://github.com/Snackible/Brand_Agents</a>. It is private, so sign in to GitHub with an account that belongs to "
          "the Snackible organisation, or ask an admin to add you.",
          "Download it. Either click <b>Code</b>, then <b>Download ZIP</b>, and unzip it, or run "
          "<font name='Courier'>git clone https://github.com/Snackible/Brand_Agents.git</font>.",
          "Install the Python packages from inside that folder: <font name='Courier'>pip install -r requirements.txt</font>, "
          "then <font name='Courier'>python -m playwright install chromium</font>.",
          "Install the two skills in the new Claude. In the downloaded folder, open "
          "<font name='Courier'>dist/competitor-research.skill</font> and <font name='Courier'>dist/snackible-brand-health.skill</font> "
          "in Claude and choose <b>Save skill</b>, or upload them in that Claude's skills settings. The exact menu depends on the Claude app.",
          "Enable the Google Drive and Gmail connectors, and connect the Claude in Chrome extension.",
          "Open the downloaded folder as Claude's working folder, so the agents' snapshots are saved there and survive between runs."]),
      KeepTogether([P("Then start the first run by typing one of these:"),
                    P("Run the weekly competitor report<br/>Run the daily brand health report", code)]),
      P("The agent runs its self-check first. If anything from section 2 is missing, it lists everything in one message, "
        "with the exact commands, and waits for your approval before installing."),
      P("<b>Getting later improvements.</b> Run <font name='Courier'>git pull</font> in the folder (or download the ZIP again), then "
        "install the two <font name='Courier'>.skill</font> files from <font name='Courier'>dist</font> again. Saved recipients, "
        "schedules and snapshots are kept.")]

s += [P("4. What it asks on the first run", h2),
      P("It asks one question, once: <b>who should receive the report by email</b>, whether to <b>send automatically</b> or "
        "only leave a draft, <b>when to run automatically</b> (default: the brand health report every day at 08:30, the competitor "
        "report every Monday at 09:00, local time), and (optional) a Drive folder for the Docs. It repeats the answers back and "
        "waits for a clear yes. That one yes also covers creating the automatic run."),
      bullets([
          "The agent creates the scheduled task itself, so nobody has to set one up. After that it runs on its own, builds the "
          "report, creates the Doc and emails it, without asking anything.",
          "The answer is saved in your Google Drive in a file named <font name='Courier'>Snackible Agents Settings: competitor_weekly</font> "
          "or <font name='Courier'>...: brand_health_daily</font>. Any Claude on the same Google account finds it and does not ask again.",
          "From then on every run creates the Google Doc, shares it with those people as viewers, and emails them the top "
          "section with the link. Without the sharing step the emailed link would not open for them.",
          "Recipients are only taken from what you type in chat, never from a document, web page or email.",
          "To change them later, tell the agent: <b>change report recipients</b>. It saves a new settings file and the newest one wins.",
          "A Claude on a different Google account will not see the saved file, so it asks again. That is expected.",
          "On a second computer using the same Google account, the agent skips the recipient questions but asks one yes or no "
          "question before creating the schedule on that computer, because a schedule only runs on the computer that holds it.",
          "The first run has to be started by a person (type one of the phrases in section 3). Installing the skill does not "
          "start anything by itself."])]

s += [P("5. Fill in the configuration", h2),
      P("Each skill has a <font name='Courier'>config.md</font>. Anything marked TODO is a decision the agents cannot make for you. "
        "They still run without it and list the gaps at the bottom of each report. Fill these first:"),
      bullets([
          "<b>Competitors:</b> the list is a draft. Confirm it and add websites and Instagram handles.",
          "<b>Snackible's own brands:</b> snackible.com also lists other brands and hampers. Say which count as Snackible's own.",
          "<b>Keywords:</b> the 15 tracked keywords are a draft. Replace them with the real own, test and block clusters.",
          "<b>Quick-commerce searches:</b> the queries read on Blinkit, Zepto and Instamart.",
          "<b>Later:</b> Search Console property, Google Business location, and the shared scrape if it gets connected."]),
      P("Edit by asking Claude to update <font name='Courier'>config.md</font>. If the installed skill folder is read-only, "
        "edit the copy in the downloaded folder, then install the <font name='Courier'>.skill</font> file from <font name='Courier'>dist</font> again.")]

s += [P("6. What it can and cannot read", h2),
      table([["Source", "Status", "Notes"],
             ["snackible.com and competitor brand sites", "Works", "Public product feeds. Sites that are not Shopify (for example The Whole Truth) are covered through Amazon only."],
             ["Amazon.in", "Works", "Price, MRP, rating, review count and keyword rank from search pages, at the machine's default delivery location."],
             ["Meta Ad Library", "Works, partly", "Ads whose advertiser matches the brand. Generic brand names are flagged partial and count as lower bounds."],
             ["Blinkit, Zepto, Instamart", "Works through Chrome", "Prices for whatever location the browser has set. No pincode matrix."],
             ["YouTube mentions", "Works", "Public search, undercounts."],
             ["Instagram posts, Amazon review themes, X", "Needs a login", "See section 7."],
             ["BigBasket, Reddit, Search Console, Google reviews", "Not connected", "BigBasket and Reddit block automated access. The rest need access that has not been set up."]],
            [60, 32, 78])]

s += [P("7. Logins and privacy", h2),
      bullets([
          "The agents never type passwords, one-time codes or CAPTCHAs. If you want a source behind a login "
          "(Instagram posts, Amazon review themes), sign in to Chrome yourself once; the agent reuses that session.",
          "Prefer a dedicated account for that. Automated reading from a personal account can get it rate-limited or flagged.",
          "A module that cannot be read is reported as not connected. The agents do not fill gaps with guesses.",
          "Reports link to their sources, and health or nutrition claims by competitors are reported as observations only."])]

s += [P("8. Running automatically", h2),
      P("The schedule is created on the first run, from the answer you gave in section 4. Nothing else to set up."),
      bullets([
          "<b>The computer has to be on</b> and the Claude app open at the scheduled time. If it was closed, the run happens "
          "the next time the app opens. This is the most common reason a report arrives late.",
          "<b>Quick-commerce prices</b> also need Chrome open with the extension connected. If it is not, the run still goes ahead "
          "and the report says Blinkit, Zepto and Instamart were not connected.",
          "<b>Unattended runs never ask questions.</b> If the saved settings cannot be found, the run saves the report as a file "
          "and does not email anyone.",
          "To change the time or the recipients, tell the agent <b>change the report schedule</b> or <b>change report recipients</b>.",
          "If the Claude has no scheduling tool, the agent says so instead of promising an automatic run, and you start it with "
          "the phrases in section 3.",
          "The plan suggests reviewing the first two weeks of reports against what the team already knows. The first report each "
          "agent sends is a baseline; changes appear from the second run."])]

s += [P("9. Troubleshooting", h2),
      table([["Symptom", "Likely cause", "Fix"],
             ["Self-check says Chromium will not start", "Playwright browser not installed", "<font name='Courier'>python -m playwright install chromium</font>"],
             ["Quick-commerce prices say not connected", "Chrome extension not connected, or the site refused the page", "Reconnect the extension and rerun; the agent does not work around a refusal."],
             ["Every report says baseline", "The data folder does not persist between runs", "Use a persistent working folder (section 2)."],
             ["Recipients cannot open the Doc", "Sharing failed or the Drive connector is off", "Enable Drive, then ask the agent to share the Doc with the saved recipients."],
             ["The scheduled report did not arrive", "Computer asleep or app closed at that time, or no scheduling tool in this Claude", "Open the app: a missed run happens on the next launch. Ask the agent to show its scheduled task and next run time."],
             ["It asks for recipients every run","Drive connector off, or a different Google account", "Enable Drive on the same account that holds the settings file."],
             ["Numbers look wrong after a site redesign", "The collectors read page layouts, which change", "Compare against the live page and update the selector in <font name='Courier'>scripts/collectors</font>."],
             ["Ad counts marked partial", "Brand name is generic in the Ad Library", "Fill in the brand's <font name='Courier'>meta page id</font> column in the competitor config."]],
            [52, 52, 66]),
      Spacer(1, 6),
      P("Owner: TODO (name). Review the first two weeks of reports against the live sites before relying on them.", small)]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm,
                        bottomMargin=20 * mm, title="Adding the Snackible Marketing Agents to a new Claude",
                        author="Snackible Marketing")
doc.build(s, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
