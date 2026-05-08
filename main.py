from fastapi import FastAPI
from gradio.routes import mount_gradio_app
from gradio_app import demo
import sqlite3

app = FastAPI(
    title="Quotes Intelligence API",
    description="Advanced Quotes Analytics Platform",
    version="2.0"
)


# -------------------------------------------------
# DATABASE
# -------------------------------------------------
def connect_db():

    connection = sqlite3.connect("quotes.db")

    connection.row_factory = sqlite3.Row

    return connection


# -------------------------------------------------
# GET ALL QUOTES
# -------------------------------------------------
@app.get("/quotes")
def get_quotes():

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM quotes")

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


# -------------------------------------------------
# GET SINGLE QUOTE
# -------------------------------------------------
@app.get("/quotes/{quote_id}")
def get_quote(quote_id: int):

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM quotes WHERE id=?",
        (quote_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row:
        return dict(row)

    return {"error": "Quote not found"}


# -------------------------------------------------
# CREATE QUOTE
# -------------------------------------------------
@app.post("/quotes")
def create_quote(
    quote: str,
    author: str,
    category: str
):

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO quotes (quote, author, category)
    VALUES (?, ?, ?)
    """, (quote, author, category))

    conn.commit()
    conn.close()

    return {
        "message": "Quote added successfully"
    }


# -------------------------------------------------
# UPDATE QUOTE
# -------------------------------------------------
@app.put("/quotes/{quote_id}")
def update_quote(
    quote_id: int,
    quote: str,
    author: str,
    category: str
):

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE quotes
    SET quote=?, author=?, category=?
    WHERE id=?
    """, (
        quote,
        author,
        category,
        quote_id
    ))

    conn.commit()
    conn.close()

    return {
        "message": "Quote updated successfully"
    }


# -------------------------------------------------
# DELETE QUOTE
# -------------------------------------------------
@app.delete("/quotes/{quote_id}")
def delete_quote(quote_id: int):

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM quotes WHERE id=?",
        (quote_id,)
    )

    conn.commit()
    conn.close()

    return {
        "message": "Quote deleted successfully"
    }


# -------------------------------------------------
# MOUNT GRADIO
# -------------------------------------------------
app = mount_gradio_app(
    app,
    demo,
    path="/gradio"
)