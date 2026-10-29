"""Builds docs/Setup_Guide_Adding_the_Agents_to_a_New_Claude.pdf (needs reportlab).

Written for a non-technical reader who will ask Claude to do the setup. The step-by-step
that Claude itself follows is SETUP_FOR_CLAUDE.md in the repository root.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

OUT = Path(__file__).parent / "Setup_Guide_Adding_the_Agents_to_a_New_Claude.pdf"
LINK = "https://github.com/Snackible/Brand_Agents"

INK = colors.HexColor("#1f2937")
MUTED = colors.HexColor("#6b7280")
ACCENT = colors.HexColor("#0f766e")
RULE = colors.HexColor("#d1d5db")
HEAD_BG = colors.HexColor("#f3f4f6")
BOX_BG = colors.HexColor("#ecfdf5")

base = getSampleStyleSheet()
body = ParagraphStyle("body", parent=base["Normal"], fontName="Helvetica", fontSize=9.8, leading=13.6,
                      textColor=INK, alignment=TA_LEFT, spaceAfter=6)
small = ParagraphStyle("small", parent=body, fontSize=8.8, leading=12, textColor=MUTED)
h1 = ParagraphStyle("h1", parent=body, fontName="Helvetica-Bold", fontSize=20, leading=24, spaceAfter=3)
sub = ParagraphStyle("sub", parent=body, fontSize=11, leading=15, textColor=MUTED, spaceAfter=8)
h2 = ParagraphStyle("h2", parent=body, fontName="Helvetica-Bold", fontSize=13, leading=17, spaceBefore=9,
                    spaceAfter=5, textColor=ACCENT, keepWithNext=True)
cell = ParagraphStyle("cell", parent=body, fontSize=9.0, leading=12, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
prompt = ParagraphStyle("prompt", parent=body, fontSize=10.4, leading=15, backColor=BOX_BG, borderColor=ACCENT,
                        borderWidth=0.8, borderPadding=(8, 9, 8, 9), spaceBefore=12, spaceAfter=10, leftIndent=6,
                        rightIndent=6)


def P(t, s=body):
    return Paragraph(t, s)


def bullets(items):
    return ListFlowable([ListItem(P(t), leftIndent=12) for t in items], bulletType="bullet", bulletFontSize=7,
                        leftIndent=12, bulletOffsetY=-1, spaceAfter=3)


def numbered(items):
    return ListFlowable([ListItem(P(t), leftIndent=16) for t in items], bulletType="1", leftIndent=16,
                        bulletFontName="Helvetica-Bold", bulletFontSize=9.8, spaceAfter=3)


def table(rows, widths):
    data = [[P(c, cellb if i == 0 else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
                           ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                           ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG)]))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(20 * mm, 11 * mm, "Snackible marketing agents: setup guide")
    canvas.drawRightString(A4[0] - 20 * mm, 11 * mm, f"Page {doc.page}")
    canvas.restoreState()


link = f"<a href='{LINK}' color='#0f766e'>{LINK}</a>"

s = [P("Setting up the Snackible marketing agents", h1),
     P("A short guide for anyone. You do not need to be technical: Claude does the setup for you and tells you when it needs "
       "a click or an answer.", sub)]

s += [P("What you get", h2),
      P("Two reports that arrive by email, with no one having to ask for them. Each email has the main points and a link to a "
        "Google Doc with the full report."),
      table([["Report", "When it arrives", "What it tells you"],
             ["Brand Health", "Every morning", "How Snackible's own products are doing: what is out of stock, prices, ratings, "
                                               "where Snackible shows up in Amazon searches. Starts with what needs attention today."],
             ["Competitor Research", "Every Monday", "What competitors changed this week: prices, offers, ads, ratings, new products."]],
            [32, 32, 106])]

s += [P("Before you start", h2),
      bullets([
          "A <b>computer you can leave on</b> in the morning, with the Claude app on it. The reports are made on that computer.",
          "A <b>Google account</b> with Drive and Gmail (your work account). The reports are saved in your Drive and emailed from your Gmail.",
          "The <b>Chrome</b> browser, if you want delivery-app prices (Blinkit, Zepto, Instamart). Everything else works without it.",
          f"<b>Access to the Snackible page on GitHub</b>: {link}. It is private. If the page says it cannot be found, ask the person "
          "who looks after Snackible's GitHub to add you."])]

s += [P("Step 1: paste this to Claude", h2),
      P("Open Claude, start a new chat, and paste the whole box below. Nothing else is needed."),
      KeepTogether([P(
          "Please set up the Snackible marketing agents for me. The instructions are in the file called "
          f"SETUP_FOR_CLAUDE.md at {LINK}. Follow them step by step and do every step yourself. Explain each step in plain "
          "words, and ask me only when you need me to click something or give you an answer. I am not technical.", prompt)])]

s += [P("Step 2: say yes and click when Claude asks", h2),
      P("Claude will work through the setup and stop only when it needs you. You can expect these, in roughly this order:"),
      numbered([
          "<b>Where to keep the files.</b> Claude suggests a folder in Documents. Say yes. Do not delete or move it later; the "
          "agents keep their history there.",
          "<b>Permission to install two small helper programs</b> the agents use to read websites. Say yes once.",
          "<b>Turning on Google Drive and Gmail</b> for Claude, if they are not on already. You click <b>Allow</b> on the Google screen.",
          "<b>Adding the Claude in Chrome extension</b>, if you want delivery-app prices. You click <b>Add to Chrome</b>.",
          "<b>One set of questions, asked once:</b> which email addresses should get the reports, whether to send them "
          "automatically or just prepare a draft, and what time. Claude repeats your answers back. Say yes, and it sets up the "
          "daily and weekly runs for you."]),
      Spacer(1, 3),
      P("Claude never types your passwords, codes or CAPTCHAs. If something needs you to sign in, it tells you what to click.")]

s += [P("Step 3: your first reports", h2),
      P("Claude then makes the first two reports. This takes about five to ten minutes. Open the emails and check them. "
        "<b>The first report of each kind is a starting picture, not a list of changes.</b> Changes appear from the second one, "
        "so a quiet first report is normal.")]

s += [P("After that", h2),
      bullets([
          "The reports arrive on their own, at the times you chose. Nothing to do.",
          "<b>The computer has to be on, and the Claude app open,</b> at that time. If it was off, the report arrives the next time "
          "the app opens. This is the most common reason a report is late.",
          "To change who gets the reports or when, tell Claude: <b>Change report recipients</b> or <b>Change the report schedule</b>.",
          "To get improvements later, tell Claude: <b>Update the Snackible agents to the latest version from GitHub.</b>",
          "For the first two weeks, compare the reports with what the team already knows, and tell Claude if something looks wrong."])]

s += [P("If something goes wrong", h2),
      table([["What happens", "What to tell Claude"],
             ["Claude cannot open the GitHub page", "The page is private. Sign in to GitHub in your browser, click the green <b>Code</b> "
                                                    "button, then <b>Download ZIP</b>, and tell Claude where the file was saved."],
             ["A report did not arrive", "\"The Snackible report did not arrive. Find out why and fix it.\" Usually the computer or "
                                         "the app was closed; it arrives when the app reopens."],
             ["Delivery-app prices are missing", "\"Check that Claude in Chrome is connected.\" Keep Chrome open when reports run."],
             ["Claude asks who gets the reports again", "\"Check that Google Drive is connected to the same Google account as before.\""],
             ["Anything else", "\"Run the setup check for the Snackible agents and fix whatever is missing.\""]],
            [62, 108])]

s += [P("Good to know", h2),
      bullets([
          "Numbers come from public web pages. Each report ends with a list of anything that could not be read, so you can see what is missing.",
          "Not covered: BigBasket and Reddit (they block automated readers). Instagram posts and Amazon review themes need you to be "
          "signed in to those sites in Chrome; Claude will tell you how if you want them.",
          "Report owner: TODO (name). Check the first two weeks of reports before relying on them."])]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm,
                        bottomMargin=20 * mm, title="Setting up the Snackible marketing agents",
                        author="Snackible Marketing")
doc.build(s, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
