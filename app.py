from flask import Flask, render_template, request, redirect, url_for, jsonify
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


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    conn.close()

    if not book:
        return "Книга не найдена", 404

    return render_template('book_detail.html', book=book)


@app.route('/book/<int:book_id>/edit')
def edit_book(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    conn.close()

    if not book:
        return "Книга не найдена", 404

    return render_template('edit_book.html', book=book)


@app.route('/book/<int:book_id>/update', methods=['POST'])
def update_book(book_id):

    title = request.form['title']
    author = request.form['author']
    category = request.form['category']
    genre = request.form.get('genre', '')
    year = request.form.get('year', '')
    cover = request.form.get('cover', '')
    description = request.form.get('description', '')

    conn = get_db_connection()

    try:
        conn.execute('''
            UPDATE books 
            SET title = ?, author = ?, category = ?, genre = ?, 
                year = ?, cover = ?, description = ?
            WHERE id = ?
        ''', (title, author, category, genre, year, cover, description, book_id))

        conn.commit()
        conn.close()

        return redirect(url_for('book_detail', book_id=book_id))

    except Exception as e:
        conn.close()
        return f"Ошибка при обновлении: {str(e)}", 500


@app.route('/book/<int:book_id>/delete')
def delete_book(book_id):
    conn = get_db_connection()

    try:
        conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
        conn.commit()
        conn.close()

        # Возвращаем на главную страницу
        return redirect(url_for('index'))

    except Exception as e:
        conn.close()
        return f"Ошибка при удалении: {str(e)}", 500


@app.route('/book/<int:book_id>/update_reading_status', methods=['POST'])
def update_reading_status(book_id):
    try:
        data = request.get_json()
        new_status = data.get('status', 'unread')

        conn = get_db_connection()
        conn.execute('UPDATE books SET reading_status = ? WHERE id = ?',
                     (new_status, book_id))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'status': new_status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # update_categories()
    app.run(debug=True)