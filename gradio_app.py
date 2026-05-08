import gradio as gr
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
import re
import random

# =================================================
# DATABASE
# =================================================
DATABASE = "quotes.db"


def load_data():

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql_query(
        "SELECT * FROM quotes",
        conn
    )

    conn.close()

    return df


# =================================================
# DASHBOARD STATS
# =================================================
def dashboard_stats():

    df = load_data()

    return (
        len(df),
        df["author"].nunique(),
        df["category"].nunique()
    )


# =================================================
# RANDOM QUOTE
# =================================================
def random_quote():

    df = load_data()

    row = df.sample(1).iloc[0]

    return f"""
<div style="
padding:25px;
border-radius:20px;
background:rgba(255,255,255,0.08);
backdrop-filter:blur(10px);
box-shadow:0 0 20px rgba(59,130,246,0.4);
">

<h2>✨ Quote of the Day</h2>

<h3>{row['quote']}</h3>

<p>👤 {row['author']}</p>

<p>🏷 {row['category']}</p>

</div>
"""


# =================================================
# SEARCH
# =================================================
def search_quotes(keyword):

    df = load_data()

    if keyword == "":
        return df

    return df[
        df["quote"].str.contains(
            keyword,
            case=False,
            na=False
        )
    ]


# =================================================
# FILTERS
# =================================================
def filter_author(author):

    df = load_data()

    return df[
        df["author"] == author
    ]


def filter_category(category):

    df = load_data()

    return df[
        df["category"] == category
    ]


def get_authors():

    df = load_data()

    return sorted(
        df["author"].unique()
    )


def get_categories():

    df = load_data()

    return sorted(
        df["category"].unique()
    )


# =================================================
# POSITIVITY
# =================================================
POSITIVE_WORDS = [
    "love",
    "life",
    "hope",
    "dream",
    "success",
    "truth",
    "happy",
    "friend"
]


def positivity_score():

    df = load_data()

    text = " ".join(df["quote"])

    score = 0

    for word in POSITIVE_WORDS:
        score += text.lower().count(word)

    return f"""
# 😊 AI Positivity Score

### {score} Positive Keywords Detected
"""


# =================================================
# MOOD DETECTOR
# =================================================
def detect_mood(text):

    text = text.lower()

    if "love" in text:
        return "❤️ Romantic"

    elif "life" in text:
        return "🌎 Philosophical"

    elif "funny" in text:
        return "😂 Humorous"

    else:
        return "✨ Inspirational"


# =================================================
# AI RECOMMENDATION
# =================================================
def recommend_quotes(user_text):

    df = load_data()

    words = set(
        user_text.lower().split()
    )

    scores = []

    for _, row in df.iterrows():

        quote_words = set(
            row["quote"].lower().split()
        )

        similarity = len(
            words.intersection(
                quote_words
            )
        )

        scores.append(
            (similarity, row["quote"])
        )

    scores = sorted(
        scores,
        reverse=True
    )

    results = [
        item[1]
        for item in scores[:5]
    ]

    return "\n\n".join(results)


# =================================================
# STOPWORDS
# =================================================
STOPWORDS = {
    "the", "and", "is", "to", "of",
    "in", "a", "that", "it", "for",
    "on", "with", "as", "this",
    "be", "are", "was", "at"
}


# =================================================
# WORD FREQUENCY
# =================================================
def word_frequency():

    df = load_data()

    text = " ".join(df["quote"])

    words = re.findall(
        r"\b\w+\b",
        text.lower()
    )

    filtered_words = [
        word for word in words
        if word not in STOPWORDS
        and len(word) > 2
    ]

    common = Counter(
        filtered_words
    ).most_common(15)

    labels = [x[0] for x in common]
    values = [x[1] for x in common]

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(labels, values)

    ax.set_title(
        "Top Keywords"
    )

    plt.xticks(rotation=45)

    return fig


# =================================================
# AUTHOR CHART
# =================================================
def author_chart():

    df = load_data()

    counts = (
        df["author"]
        .value_counts()
        .head(10)
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    counts.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Top Authors"
    )

    plt.xticks(rotation=45)

    return fig


# =================================================
# CATEGORY CHART
# =================================================
def category_chart():

    df = load_data()

    counts = (
        df["category"]
        .value_counts()
    )

    fig, ax = plt.subplots(figsize=(6, 6))

    counts.plot(
        kind="pie",
        autopct="%1.1f%%",
        ax=ax
    )

    ax.set_ylabel("")

    ax.set_title(
        "Category Distribution"
    )

    return fig


# =================================================
# WORDCLOUD
# =================================================
def generate_wordcloud():

    df = load_data()

    text = " ".join(df["quote"])

    wc = WordCloud(
        width=1200,
        height=600,
        background_color="black",
        colormap="plasma"
    ).generate(text)

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.imshow(wc)

    ax.axis("off")

    return fig


# =================================================
# EXPORT CSV
# =================================================
def export_csv():

    df = load_data()

    file_name = "quotes_export.csv"

    df.to_csv(
        file_name,
        index=False
    )

    return file_name


# =================================================
# CUSTOM CSS
# =================================================
CUSTOM_CSS = """
body {
    background:#020617;
}

.gradio-container {
    background:linear-gradient(
        to right,
        #020617,
        #0f172a
    );
    color:white;
}

footer {
    visibility:hidden;
}

button {
    border-radius:15px !important;
    background:#2563eb !important;
    color:white !important;
}

textarea, input {
    border-radius:15px !important;
}

"""


# =================================================
# UI
# =================================================
def create_dashboard():

    with gr.Blocks(
        css=CUSTOM_CSS,
        title="AI Quote Intelligence Platform"
    ) as demo:

        # HERO IMAGE
        gr.Image(
            value="https://images.unsplash.com/photo-1516321318423-f06f85e504b3",
            height=280,
            show_label=False,
            interactive=False
        )

        # HEADER
        gr.Markdown("""
# 🚀 AI Quote Intelligence Platform

### Advanced NLP-style Analytics Dashboard

Analyze quotes with:
- FastAPI
- Gradio
- SQLite
- AI-style Text Analysis
- Interactive Visualizations
""")

        # =================================================
        # TABS
        # =================================================
        with gr.Tabs():

            # =============================================
            # DASHBOARD
            # =============================================
            with gr.Tab("🏠 Dashboard"):

                gr.Markdown(
                    "## 📊 Platform Overview"
                )

                with gr.Row():

                    total_quotes = gr.Number(
                        label="📚 Quotes"
                    )

                    total_authors = gr.Number(
                        label="👤 Authors"
                    )

                    total_categories = gr.Number(
                        label="🏷 Categories"
                    )

                demo.load(
                    dashboard_stats,
                    outputs=[
                        total_quotes,
                        total_authors,
                        total_categories
                    ]
                )

                gr.Markdown("---")

                random_output = gr.Markdown()

                random_btn = gr.Button(
                    "✨ Generate Smart Quote"
                )

                random_btn.click(
                    random_quote,
                    outputs=random_output
                )

                demo.load(
                    random_quote,
                    outputs=random_output
                )

            # =============================================
            # SEARCH
            # =============================================
            with gr.Tab("🔎 Search Engine"):

                gr.Markdown(
                    "## 🔍 Intelligent Search"
                )

                with gr.Row():

                    keyword = gr.Textbox(
                        label="Search Quotes"
                    )

                    search_btn = gr.Button(
                        "Search"
                    )

                search_output = gr.Dataframe()

                search_btn.click(
                    search_quotes,
                    inputs=keyword,
                    outputs=search_output
                )

                gr.Markdown("---")

                gr.Markdown(
                    "## 🎯 Advanced Filters"
                )

                with gr.Row():

                    author_dropdown = gr.Dropdown(
                        choices=get_authors(),
                        label="Author"
                    )

                    category_dropdown = gr.Dropdown(
                        choices=get_categories(),
                        label="Category"
                    )

                with gr.Row():

                    author_btn = gr.Button(
                        "Filter Author"
                    )

                    category_btn = gr.Button(
                        "Filter Category"
                    )

                author_output = gr.Dataframe()
                category_output = gr.Dataframe()

                author_btn.click(
                    filter_author,
                    inputs=author_dropdown,
                    outputs=author_output
                )

                category_btn.click(
                    filter_category,
                    inputs=category_dropdown,
                    outputs=category_output
                )

            # =============================================
            # ANALYTICS
            # =============================================
            with gr.Tab("📈 Analytics"):

                gr.Markdown(
                    "## 📊 Data Visualization"
                )

                with gr.Row():

                    btn_authors = gr.Button(
                        "Top Authors"
                    )

                    btn_category = gr.Button(
                        "Category Distribution"
                    )

                with gr.Row():

                    plot1 = gr.Plot()
                    plot2 = gr.Plot()

                btn_authors.click(
                    author_chart,
                    outputs=plot1
                )

                btn_category.click(
                    category_chart,
                    outputs=plot2
                )

                gr.Markdown("---")

                gr.Markdown(
                    "## 🧠 NLP Analysis"
                )

                with gr.Row():

                    btn_words = gr.Button(
                        "Keyword Frequency"
                    )

                    btn_cloud = gr.Button(
                        "Generate WordCloud"
                    )

                with gr.Row():

                    plot3 = gr.Plot()
                    plot4 = gr.Plot()

                btn_words.click(
                    word_frequency,
                    outputs=plot3
                )

                btn_cloud.click(
                    generate_wordcloud,
                    outputs=plot4
                )

            # =============================================
            # AI INSIGHTS
            # =============================================
            with gr.Tab("🤖 AI Insights"):

                gr.Markdown(
                    "## 😊 AI Sentiment Analysis"
                )

                positivity_output = gr.Markdown()

                positivity_btn = gr.Button(
                    "Analyze Positivity"
                )

                positivity_btn.click(
                    positivity_score,
                    outputs=positivity_output
                )

                gr.Markdown("---")

                gr.Markdown(
                    "## 🎭 Mood Detector"
                )

                mood_input = gr.Textbox(
                    label="Enter Text"
                )

                mood_output = gr.Textbox()

                mood_btn = gr.Button(
                    "Detect Mood"
                )

                mood_btn.click(
                    detect_mood,
                    inputs=mood_input,
                    outputs=mood_output
                )

                gr.Markdown("---")

                gr.Markdown(
                    "## 🤖 AI Quote Recommendation"
                )

                recommend_input = gr.Textbox(
                    label="Enter Topic"
                )

                recommend_output = gr.Textbox(
                    lines=10
                )

                recommend_btn = gr.Button(
                    "Recommend Quotes"
                )

                recommend_btn.click(
                    recommend_quotes,
                    inputs=recommend_input,
                    outputs=recommend_output
                )

            # =============================================
            # EXPORT
            # =============================================
            with gr.Tab("⬇ Export Center"):

                gr.Markdown(
                    "## 📄 Dataset"
                )

                gr.Dataframe(
                    value=load_data(),
                    interactive=False
                )

                gr.Markdown("---")

                gr.Markdown(
                    "## ⬇ Download CSV"
                )

                export_btn = gr.Button(
                    "Export Dataset"
                )

                export_file = gr.File()

                export_btn.click(
                    export_csv,
                    outputs=export_file
                )

        # FOOTER
        gr.Markdown("""
---
# ⚡ AI-Powered Analytics Platform

Built with FastAPI + Gradio + SQLite
""")

    return demo


# =================================================
# CREATE DEMO
# =================================================
demo = create_dashboard()