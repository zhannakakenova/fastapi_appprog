# crawler.py

import sqlite3
import requests
from bs4 import BeautifulSoup
from time import sleep

# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------
BASE_URL = "https://quotes.toscrape.com"

CATEGORIES = [
    "love",
    "life",
    "humor",
    "inspirational"
]

MAX_QUOTES_PER_CATEGORY = 20

DATABASE_NAME = "quotes.db"


# -------------------------------------------------
# DATABASE SETUP
# -------------------------------------------------
def initialize_database():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quote TEXT NOT NULL,
        author TEXT NOT NULL,
        category TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS unique_quote_index
    ON quotes (quote, author, category)
    """)

    connection.commit()

    return connection, cursor


# -------------------------------------------------
# CLEAR DATABASE
# -------------------------------------------------
def clear_old_data(cursor):

    cursor.execute("DELETE FROM quotes")


# -------------------------------------------------
# SAVE QUOTE
# -------------------------------------------------
def save_quote(cursor, quote, author, category):

    cursor.execute("""
    INSERT OR IGNORE INTO quotes
    (quote, author, category)
    VALUES (?, ?, ?)
    """, (
        quote,
        author,
        category
    ))


# -------------------------------------------------
# PARSE QUOTES
# -------------------------------------------------
def parse_quotes(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    quote_blocks = soup.find_all(
        "div",
        class_="quote"
    )

    parsed_quotes = []

    for block in quote_blocks:

        quote_text = block.find(
            "span",
            class_="text"
        ).get_text(strip=True)

        author_name = block.find(
            "small",
            class_="author"
        ).get_text(strip=True)

        parsed_quotes.append({
            "quote": quote_text,
            "author": author_name
        })

    return parsed_quotes


# -------------------------------------------------
# CRAWL CATEGORY
# -------------------------------------------------
def crawl_category(category, cursor):

    current_page = 1
    total_collected = 0

    print(f"\n📚 Crawling category: {category}")

    while total_collected < MAX_QUOTES_PER_CATEGORY:

        url = f"{BASE_URL}/tag/{category}/page/{current_page}/"

        try:

            response = requests.get(
                url,
                timeout=10
            )

            if response.status_code != 200:
                print(f"⚠️ Page not found: {url}")
                break

            quotes = parse_quotes(response.text)

            if not quotes:
                break

            for item in quotes:

                save_quote(
                    cursor,
                    item["quote"],
                    item["author"],
                    category
                )

                total_collected += 1

                if total_collected >= MAX_QUOTES_PER_CATEGORY:
                    break

            print(
                f"✅ Page {current_page} completed "
                f"| Total collected: {total_collected}"
            )

            current_page += 1

            sleep(0.5)

        except Exception as error:

            print(f"❌ Error while crawling: {error}")

            break


# -------------------------------------------------
# MAIN FUNCTION
# -------------------------------------------------
def main():

    print("\n🚀 Starting Quotes Crawler...\n")

    connection, cursor = initialize_database()

    # Remove old records before crawling
    clear_old_data(cursor)

    for category in CATEGORIES:

        crawl_category(
            category,
            cursor
        )

    connection.commit()

    connection.close()

    print("\n🎉 Database updated successfully!")
    print("📦 quotes.db is ready.")


# -------------------------------------------------
# RUN SCRIPT
# -------------------------------------------------
if __name__ == "__main__":

    main()