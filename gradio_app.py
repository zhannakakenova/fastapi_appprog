import os
import sqlite3
import random
import pandas as pd
import gradio as gr

# ==========================================
# DATABASE
# ==========================================
DATABASE = "quotes.db"


def load_data():

    try:
        conn = sqlite3.connect(DATABASE)

        df = pd.read_sql_query(
            "SELECT * FROM quotes",
            conn
        )

        conn.close()

        return df

    except Exception as e:

        print("DATABASE ERROR:", e)

        return pd.DataFrame({
            "quote": [
                "Believe in yourself.",
                "Dream big.",
                "Stay positive."
            ],
            "author": [
                "Unknown",
                "Unknown",
                "Unknown"
            ],
            "category": [
                "Motivation",
                "Success",
                "Life"
            ]
        })


# ==========================================
# STATS
# ==========================================
def get_stats():

    df = load_data()

    return (
        len(df),
        df["author"].nunique(),
        df["category"].nunique()
    )


# ==========================================
# RANDOM QUOTE
# ==========================================
def random_quote():

    df = load_data()

    row = df.sample(1).iloc[0]

    return f"""
# ✨ Quote of the Day

> {row['quote']}

👤 **{row['author']}**

🏷 **{row['category']}**
"""


# ==========================================
# SEARCH
# ==========================================
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


# ==========================================
# FILTERS
# ==========================================
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


# ==========================================
# EXPORT CSV
# ==========================================
def export_csv():

    df = load_data()

    file_name = "quotes_export.csv"

    df.to_csv(
        file_name,
        index=False
    )

    return file_name


# ==========================================
# CUSTOM CSS
# ==========================================
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
    border-radius:14px !important;
    background:#2563eb !important;
    color:white !important;
}

"""


# ==========================================
# UI
# ==========================================
with gr.Blocks(
    css=CUSTOM_CSS,
    title="AI Quote Dashboard"
) as demo:

    # HERO
    gr.HTML("""
    <div style="
        width:100%;
        border-radius:24px;
        overflow:hidden;
        margin-bottom:20px;
        box-shadow:0 10px 30px rgba(0,0,0,0.35);
    ">

    <img
        src="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=1600&auto=format&fit=crop"
        style="
            width:100%;
            height:300px;
            object-fit:cover;
            display:block;
        "
    />

    </div>
    """)

    # HEADER
    gr.Markdown("""
# 🚀 AI Quote Intelligence Dashboard

Analyze quotes with:
- Gradio
- SQLite
- Smart Search
- CSV Export
- Interactive Dashboard
""")

    # ======================================
    # DASHBOARD
    # ======================================
    with gr.Tab("📊 Dashboard"):

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
            get_stats,
            outputs=[
                total_quotes,
                total_authors,
                total_categories
            ]
        )

        gr.Markdown("---")

        quote_output = gr.Markdown()

        quote_btn = gr.Button(
            "✨ Generate Quote"
        )

        quote_btn.click(
            random_quote,
            outputs=quote_output
        )

        demo.load(
            random_quote,
            outputs=quote_output
        )

    # ======================================
    # SEARCH
    # ======================================
    with gr.Tab("🔍 Search"):

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

    # ======================================
    # FILTERS
    # ======================================
    with gr.Tab("🎯 Filters"):

        author_dropdown = gr.Dropdown(
            choices=get_authors(),
            label="Author"
        )

        author_btn = gr.Button(
            "Filter Author"
        )

        author_output = gr.Dataframe()

        author_btn.click(
            filter_author,
            inputs=author_dropdown,
            outputs=author_output
        )

        gr.Markdown("---")

        category_dropdown = gr.Dropdown(
            choices=get_categories(),
            label="Category"
        )

        category_btn = gr.Button(
            "Filter Category"
        )

        category_output = gr.Dataframe()

        category_btn.click(
            filter_category,
            inputs=category_dropdown,
            outputs=category_output
        )

    # ======================================
    # EXPORT
    # ======================================
    with gr.Tab("⬇ Export"):

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


# ==========================================
# START APP
# ==========================================
if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 7860)
    )

    demo.launch(
        server_name="0.0.0.0",
        server_port=port
    )