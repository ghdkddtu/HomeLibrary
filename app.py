from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DATABASE = 'library.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def update_categories():
    conn = get_db_connection()

    updates = {
        'Для души': 'Художественные',
        'Справочники': 'Познавательные'
    }

    for old_cat, new_cat in updates.items():
        conn.execute('UPDATE books SET category = ? WHERE category = ?',
                     (new_cat, old_cat))

    conn.execute("UPDATE books SET category = 'Другое' WHERE category = 'Работа'")

    conn.commit()
    conn.close()
    print("Категории обновлены!")

@app.route('/')
def index():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()

    return render_template('index.html', books=books)



@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        category = request.form['category']
        genre = request.form['genre']
        year = request.form['year']
        description = request.form['description']

        conn = get_db_connection()
        conn.execute('''INSERT INTO books 
                       (title, author, category, genre, year, description) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (title, author, category, genre, year, description))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add_book.html')


if __name__ == '__main__':
    #update_categories()
    app.run(debug=True)