import os
import re
import sqlite3
from collections import Counter

import gradio as gr
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

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
## ✨ Quote of the Day

> {row['quote']}

👤 **{row['author']}**

🏷 **{row['category']}**
"""


# =================================================
# SEARCH
# =================================================
def search_quotes(keyword):

    df = load_data()

    if not keyword:
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
        df["author"].dropna().unique()
    )


def get_categories():

    df = load_data()

    return sorted(
        df["category"].dropna().unique()
    )


# =================================================
# POSITIVITY SCORE
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

    text = " ".join(df["quote"].astype(str))

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
# RECOMMENDATIONS
# =================================================
def recommend_quotes(user_text):

    df = load_data()

    words = set(
        user_text.lower().split()
    )

    scores = []

    for _, row in df.iterrows():

        quote_words = set(
            str(row["quote"]).lower().split()
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
# WORD FREQUENCY
# =================================================
STOPWORDS = {
    "the", "and", "is", "to", "of",
    "in", "a", "that", "it", "for",
    "on", "with", "as", "this",
    "be", "are", "was", "at"
}


def word_frequency():

    df = load_data()

    text = " ".join(
        df["quote"].astype(str)
    )

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

    ax.set_title("Top Keywords")

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
# WORD CLOUD
# =================================================
def generate_wordcloud():

    df = load_data()

    text = " ".join(
        df["quote"].astype(str)
    )

    wc = WordCloud(
        width=1200,
        height=600,
        background_color="black"
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
# UI
# =================================================
with gr.Blocks(
    title="AI Quote Intelligence Platform"
) as demo:

    gr.Markdown("""
# 🚀 AI Quote Intelligence Platform

Analyze quotes with:
- Gradio
- SQLite
- NLP-style Analytics
- Interactive Visualizations
""")

    with gr.Tabs():

        # DASHBOARD
        with gr.Tab("Dashboard"):

            with gr.Row():

                total_quotes = gr.Number(
                    label="Quotes"
                )

                total_authors = gr.Number(
                    label="Authors"
                )

                total_categories = gr.Number(
                    label="Categories"
                )

            demo.load(
                dashboard_stats,
                outputs=[
                    total_quotes,
                    total_authors,
                    total_categories
                ]
            )

            random_output = gr.Markdown()

            random_btn = gr.Button(
                "Generate Quote"
            )

            random_btn.click(
                random_quote,
                outputs=random_output
            )

            demo.load(
                random_quote,
                outputs=random_output
            )

        # SEARCH
        with gr.Tab("Search"):

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

        # ANALYTICS
        with gr.Tab("Analytics"):

            btn_authors = gr.Button(
                "Top Authors"
            )

            btn_category = gr.Button(
                "Category Distribution"
            )

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

            btn_words = gr.Button(
                "Keyword Frequency"
            )

            btn_cloud = gr.Button(
                "Generate WordCloud"
            )

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

        # AI
        with gr.Tab("AI Insights"):

            positivity_output = gr.Markdown()

            positivity_btn = gr.Button(
                "Analyze Positivity"
            )

            positivity_btn.click(
                positivity_score,
                outputs=positivity_output
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

        # EXPORT
        with gr.Tab("Export"):

            gr.Dataframe(
                value=load_data(),
                interactive=False
            )

            export_btn = gr.Button(
                "Export CSV"
            )

            export_file = gr.File()

            export_btn.click(
                export_csv,
                outputs=export_file
            )


# =================================================
# RAILWAY START
# =================================================
if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 7860)
    )

    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=True
    )