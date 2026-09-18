# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    ListFlowable, ListItem, HRFlowable
)

OUT = "/home/claude/FORESIGHT/docs/FORESIGHT_Project_Documentation.pdf"

doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    topMargin=1.5*cm, bottomMargin=1.5*cm,
    leftMargin=1.8*cm, rightMargin=1.8*cm
)

styles = getSampleStyleSheet()
navy = colors.HexColor("#1F3864")
accent = colors.HexColor("#2E75B6")
lightband = colors.HexColor("#EAF1FA")
green = colors.HexColor("#2E7D32")
red = colors.HexColor("#C0392B")
orange = colors.HexColor("#E67E22")
darktext = colors.HexColor("#222222")

title_style = ParagraphStyle("TitleBig", parent=styles["Title"], fontSize=23, textColor=navy, alignment=TA_CENTER, spaceAfter=6)
subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=12.5, textColor=accent, alignment=TA_CENTER, spaceAfter=4)
meta_style = ParagraphStyle("Meta", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#555555"), alignment=TA_CENTER)
h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=15, textColor=navy, spaceBefore=14, spaceAfter=8)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, textColor=accent, spaceBefore=10, spaceAfter=4)
body = ParagraphStyle("Body2", parent=styles["Normal"], fontSize=10.2, textColor=darktext, leading=14.5, alignment=TA_LEFT)
body_bold = ParagraphStyle("BodyBold", parent=body, fontName="Helvetica-Bold")
cell = ParagraphStyle("Cell", parent=body, fontSize=9.2, leading=12.5)
cell_head = ParagraphStyle("CellHead", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)
mono = ParagraphStyle("Mono", parent=body, fontName="Courier", fontSize=8.8, backColor=colors.HexColor("#F4F4F4"), leading=12, leftIndent=6, spaceBefore=4, spaceAfter=4)

story = []

def hr():
    return HRFlowable(width="100%", thickness=0.8, color=accent, spaceBefore=4, spaceAfter=10)

def section(title):
    story.append(Paragraph(title, h1))

def subsection(title):
    story.append(Paragraph(title, h2))

def para(text):
    story.append(Paragraph(text, body))
    story.append(Spacer(1, 0.15*cm))

def bullets(items):
    story.append(ListFlowable([ListItem(Paragraph(t, body), bulletColor=accent) for t in items],
                               bulletType="bullet", start="circle", leftIndent=14))
    story.append(Spacer(1, 0.15*cm))

# ================= COVER =================
story.append(Spacer(1, 1.5*cm))
story.append(Paragraph("Project FORESIGHT", title_style))
story.append(Paragraph("AI-Powered Demand Forecasting &amp; Inventory Intelligence Platform", subtitle_style))
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph("Complete Project Documentation", ParagraphStyle("st2", parent=subtitle_style, fontSize=13.5, textColor=navy, fontName="Helvetica-Bold")))
story.append(Spacer(1, 0.6*cm))
line_tbl = Table([[""]], colWidths=[17*cm], rowHeights=[0.06*cm])
line_tbl.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), accent)]))
story.append(line_tbl)
story.append(Spacer(1, 0.5*cm))
story.append(Paragraph("Assigned: 20 August 2026 &nbsp;|&nbsp; Submission Deadline: 20 September 2026", meta_style))
story.append(Spacer(1, 1.2*cm))

overview_pts = [
    "Predicts SKU-level product demand for the next 8 weeks using time-series forecasting.",
    "Automatically flags SKUs at risk of stockout or overstock based on forecast vs. current stock.",
    "Recommends exact reorder quantities for at-risk SKUs using a standard inventory formula.",
    "Presents everything on an interactive Streamlit dashboard with charts and colour-coded risk tables.",
    "Fully tested end-to-end, including a simulated fresh-clone run, with zero runtime errors.",
]
subsection("What This Project Does")
bullets(overview_pts)

subsection("What's Included")
included = [
    "Complete, working source code across 5 connected pipeline stages + dashboard",
    "A synthetic but realistic dataset (25 SKUs, 2 years of weekly data)",
    "One-command pipeline runner (run_pipeline.py)",
    "requirements.txt with exact tested versions",
    "README.md with setup instructions, ready for GitHub",
    "This documentation PDF, explaining every technology choice",
]
bullets(included)

story.append(PageBreak())

# ================= ARCHITECTURE =================
section("1. How the Project Is Structured")
para(
    "FORESIGHT is built as five connected stages that each read from and write to a shared "
    "database, followed by a dashboard that only reads from that database. This means each "
    "stage can be tested, re-run, or explained independently, while <b>run_pipeline.py</b> ties "
    "all five together into a single command for a clean demo."
)

flow_data = [
    [Paragraph("Stage", cell_head), Paragraph("File", cell_head), Paragraph("Input &rarr; Output", cell_head)],
    [Paragraph("1. Data Cleaning", cell), Paragraph("src/data_cleaning.py", cell), Paragraph("Raw messy CSV &rarr; Clean CSV", cell)],
    [Paragraph("2. Database Setup", cell), Paragraph("src/database.py", cell), Paragraph("Clean CSV &rarr; sales_history table", cell)],
    [Paragraph("3. Forecasting", cell), Paragraph("src/forecasting.py", cell), Paragraph("sales_history &rarr; forecast_results table", cell)],
    [Paragraph("4. Risk Detection", cell), Paragraph("src/risk_detection.py", cell), Paragraph("forecast_results + stock &rarr; risk_alerts table", cell)],
    [Paragraph("5. Recommendations", cell), Paragraph("src/recommendation.py", cell), Paragraph("risk_alerts &rarr; recommendations table", cell)],
    [Paragraph("Dashboard", cell), Paragraph("dashboard/app.py", cell), Paragraph("Reads all 4 tables &rarr; interactive UI", cell)],
]
t = Table(flow_data, colWidths=[3.6*cm, 4.6*cm, 8.8*cm], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), navy),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#BBBBBB")),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, lightband]),
    ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
]))
story.append(t)
story.append(Spacer(1, 0.4*cm))

# ================= TECH STACK =================
section("2. Technology Stack — What, and Why")

tech_rows = [
    ("Python", "Core language for the entire pipeline", "One consistent language across data cleaning, modelling, database access and the dashboard; the standard choice for a data science project."),
    ("Pandas &amp; NumPy", "Data cleaning, transformation, feature prep", "Industry-standard tabular data tools; used for deduplication, imputation, outlier handling and time-series reshaping."),
    ("statsmodels (ARIMA)", "Demand forecasting model", "ARIMA is a well-established, explainable time-series model suited to weekly sales data with trend and seasonality. Being explainable matters for a viva/interview: you can describe exactly what the model is doing, unlike a black-box model."),
    ("SQLite", "Database (used in this build)", "Zero-setup, file-based database with no server or credentials needed. Chosen specifically so the project runs identically on any machine during testing, grading, or a recorded demo, with no 'database connection failed' risk."),
    ("MySQL (documented path)", "Production database (see docs/schema_mysql.sql)", "The originally intended production database. All database access is isolated behind one function (get_connection()), so switching from SQLite to MySQL later only means changing that one function; every other file stays the same."),
    ("Streamlit", "Interactive dashboard", "Builds a genuinely interactive web dashboard in pure Python with no separate HTML/CSS/JS needed, ideal for a fast, demoable data science front-end."),
    ("Plotly", "Charts inside the dashboard", "Interactive (zoomable, hoverable) charts, which present a forecast far better in a live demo than a static image."),
]

tech_data = [[Paragraph("Technology", cell_head), Paragraph("Used For", cell_head), Paragraph("Why This Choice", cell_head)]]
for name, use, why in tech_rows:
    tech_data.append([Paragraph(name, cell), Paragraph(use, cell), Paragraph(why, cell)])

t2 = Table(tech_data, colWidths=[3.4*cm, 4.4*cm, 9.2*cm], repeatRows=1)
t2.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), navy),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#BBBBBB")),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, lightband]),
    ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
]))
story.append(t2)
story.append(PageBreak())

# ================= STAGE-BY-STAGE DETAIL =================
section("3. Stage-by-Stage Explanation")

subsection("3.1 Dataset")
para(
    "A synthetic dataset covering 25 SKUs across 5 categories (Electronics, Grocery, Apparel, "
    "Home &amp; Kitchen, Beauty), with 104 weeks (2 years) of sales and stock data per SKU, "
    "including real trend, seasonality, and promotion effects. It is deliberately messy in the "
    "same way a real retail export is: missing values, duplicate rows, inconsistent text "
    "casing, mixed date formats, outliers, and impossible entries like negative stock or zero "
    "price. This gives the cleaning stage genuine work to do rather than operating on "
    "already-clean data, which is more representative of a real project."
)

subsection("3.2 Data Cleaning &mdash; src/data_cleaning.py")
para("<b>What it does:</b>")
bullets([
    "Standardises text (casing, whitespace) and parses mixed date formats into one consistent format",
    "Removes exact duplicate rows",
    "Treats impossible values (negative stock, zero price) as missing, then imputes them",
    "Caps extreme outliers in Units_Sold using the IQR method, so a data-entry error doesn't distort a SKU's forecast",
    "Imputes remaining missing values per-SKU using that SKU's own median, so a low-selling item isn't filled with a high-selling item's typical value",
])
para("<b>Why this matters:</b> forecasting models are sensitive to bad input &mdash; an unparsed date or a stray missing week can silently break a whole time series. Cleaning first means every later stage can trust the data it receives.")

subsection("3.3 Database &mdash; src/database.py")
para("<b>What it does:</b> Creates four tables and loads the cleaned data into the first one:")
bullets([
    "<b>sales_history</b> &mdash; the cleaned weekly sales &amp; stock records",
    "<b>forecast_results</b> &mdash; the forecasting stage's output",
    "<b>risk_alerts</b> &mdash; the risk detection stage's output",
    "<b>recommendations</b> &mdash; the recommendation engine's output",
])
para(
    "<b>Why SQLite:</b> it needs no server installation or login credentials, so the exact same "
    "code runs on any machine &mdash; yours, an evaluator's, or during a recorded demo &mdash; "
    "without any environment-specific setup that could fail on the day. All database access goes "
    "through one function, get_connection(), so upgrading to a real MySQL server later (schema "
    "provided in docs/schema_mysql.sql) is a one-function change, not a rewrite."
)

subsection("3.4 Forecasting &mdash; src/forecasting.py")
para(
    "Fits an ARIMA(1,1,1) model per SKU using statsmodels, forecasting 8 weeks ahead. Each "
    "model is first validated on a held-out window (its own last 8 weeks) to compute MAE "
    "(Mean Absolute Error) and RMSE (Root Mean Squared Error), so forecast quality is measured, "
    "not just assumed."
)
para(
    "<b>Reliability safeguard:</b> if ARIMA fails to converge for a particular SKU (this can "
    "genuinely happen with short or irregular series), the code automatically falls back to a "
    "weighted moving average for that SKU only. This means one difficult SKU can never crash "
    "the whole pipeline &mdash; important for a live demo where a crash mid-run would be very "
    "visible."
)

subsection("3.5 Risk Detection &mdash; src/risk_detection.py")
para(
    "For each SKU, compares current stock against forecasted demand over that SKU's own "
    "lead-time window, and classifies it:"
)
bullets([
    "<b>Stockout risk</b> &mdash; current stock is below forecasted demand for the lead-time window",
    "<b>Overstock risk</b> &mdash; current stock is more than 3&times; the forecasted demand for that window",
    "<b>Normal</b> &mdash; stock is within a healthy range",
])
para(
    "Each is further scored High/Medium/Low based on how far past the threshold it is. "
    "<b>Why rule-based rather than a machine-learning classifier:</b> a business user needs to "
    "be able to ask 'why is this flagged?' and get a clear answer. A transparent formula is "
    "more trustworthy, auditable, and easier to defend in a project viva than a black-box model "
    "for what is fundamentally a threshold decision."
)

subsection("3.6 Recommendation Engine &mdash; src/recommendation.py")
para("Uses the standard inventory management formula for any SKU flagged as Stockout risk:")
story.append(Paragraph(
    "Reorder Quantity&nbsp;=&nbsp;Forecasted demand (lead time)&nbsp;+&nbsp;Safety stock&nbsp;&minus;&nbsp;Current stock",
    mono
))
para(
    "Safety stock is set at 50% of the lead-time demand, as a buffer against demand variability "
    "so the SKU isn't reordered down to the bare minimum. Overstock SKUs instead get a "
    "'hold off ordering' recommendation. <b>Why this matters:</b> a forecast and a risk flag "
    "tell you there's a problem; this is the layer that tells you exactly what to do about it "
    "&mdash; the actual decision-support value of an 'inventory intelligence' platform, as "
    "opposed to a plain reporting tool."
)

subsection("3.7 Dashboard &mdash; dashboard/app.py")
para(
    "A Streamlit app showing: four KPI summary cards (total SKUs, stockout count, overstock "
    "count, SKUs needing reorder), a per-SKU actual-vs-forecast chart built with Plotly, a "
    "colour-coded risk table across all SKUs, and a forecast accuracy (MAE/RMSE) table. It only "
    "reads from the database &mdash; all computation already happened in the pipeline stages "
    "&mdash; which keeps the dashboard fast and simple."
)

story.append(PageBreak())

# ================= RESULTS =================
section("4. Verified Results (From an Actual Pipeline Run)")
results_data = [
    [Paragraph("Metric", cell_head), Paragraph("Result", cell_head)],
    [Paragraph("Rows in raw dataset", cell), Paragraph("2,652 (25 SKUs &times; 104 weeks + injected duplicates)", cell)],
    [Paragraph("Duplicate rows removed", cell), Paragraph("52", cell)],
    [Paragraph("Outliers capped (IQR method)", cell), Paragraph("12", cell)],
    [Paragraph("Missing values after cleaning", cell), Paragraph("0", cell)],
    [Paragraph("SKUs successfully forecasted", cell), Paragraph("25 / 25 (all via ARIMA(1,1,1))", cell)],
    [Paragraph("Average forecast MAE / RMSE", cell), Paragraph("38.4 / 53.1 units per week", cell)],
    [Paragraph("Risk mix detected", cell), Paragraph("11 Normal, 8 Overstock, 6 Stockout", cell)],
    [Paragraph("SKUs with an active reorder recommendation", cell), Paragraph("6", cell)],
]
t3 = Table(results_data, colWidths=[8*cm, 9*cm], repeatRows=1)
t3.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), navy),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#BBBBBB")),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, lightband]),
    ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
]))
story.append(t3)
story.append(Spacer(1, 0.3*cm))

subsection("How This Was Tested")
bullets([
    "Every module (data_cleaning, database, forecasting, risk_detection, recommendation) was run individually and verified for correct output before being connected.",
    "The full pipeline (run_pipeline.py) was run start-to-finish with zero errors.",
    "The dashboard was tested using Streamlit's official AppTest framework, which actually executes the app script and reports any runtime exception &mdash; result: no exceptions.",
    "The entire project folder was copied to a separate location, all generated files (database, cleaned CSV) were deleted, and the whole pipeline plus dashboard were re-run from that clean copy to simulate exactly what happens after a fresh 'git clone' &mdash; it completed with zero errors.",
])

story.append(PageBreak())

# ================= HOW TO RUN =================
section("5. How to Run This Project")
story.append(Paragraph("1. Install dependencies:", body_bold))
story.append(Paragraph("pip install -r requirements.txt", mono))
story.append(Paragraph("2. Run the full pipeline (cleans data, builds the database, forecasts, detects risk, generates recommendations):", body_bold))
story.append(Paragraph("python run_pipeline.py", mono))
story.append(Paragraph("3. Launch the dashboard:", body_bold))
story.append(Paragraph("streamlit run dashboard/app.py", mono))
para("Three commands, no external server, no API keys, no manual configuration required.")

subsection("Putting This on GitHub")
story.append(Paragraph(
    "git init<br/>git add .<br/>"
    "git commit -m \"Initial commit: FORESIGHT demand forecasting &amp; inventory intelligence platform\"<br/>"
    "git branch -M main<br/>git remote add origin &lt;your-repo-url&gt;<br/>git push -u origin main",
    mono
))
para(
    "The generated database file and cleaned CSV are excluded via .gitignore since they are "
    "fully reproducible &mdash; anyone cloning the repository just runs run_pipeline.py once to "
    "regenerate them."
)

subsection("Project Folder Structure")
story.append(Paragraph(
    "FORESIGHT/<br/>"
    "&nbsp;&nbsp;data/ &mdash; dataset generator, raw and (generated) clean CSVs, database file<br/>"
    "&nbsp;&nbsp;src/ &mdash; the five pipeline stage modules<br/>"
    "&nbsp;&nbsp;dashboard/app.py &mdash; the Streamlit dashboard<br/>"
    "&nbsp;&nbsp;docs/schema_mysql.sql &mdash; MySQL production schema reference<br/>"
    "&nbsp;&nbsp;run_pipeline.py &mdash; runs all five stages in order<br/>"
    "&nbsp;&nbsp;requirements.txt, README.md, .gitignore",
    mono
))

doc.build(story)
print("PDF built at", OUT)
