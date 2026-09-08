from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, session
import sqlite3
import os

app = Flask("NisprohoKobiShomogro")
app.secret_key = "nisproho_secure_library_key_2026"

UPLOAD_FOLDER = 'static/uploads'
DB_NAME = 'library.db'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS publications (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, writer_name TEXT NOT NULL, category TEXT NOT NULL, description TEXT, caption TEXT, filename TEXT NOT NULL, cover_image TEXT NOT NULL, likes INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, book_id INTEGER, user_name TEXT NOT NULL, comment TEXT NOT NULL, FOREIGN KEY (book_id) REFERENCES publications (id))''')
    conn.commit()
    conn.close()

init_db()

WEB_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>নিঃস্ব্রহ কবি সমগ্র - কাব্য, উপন্যাস ও সাহিত্যের ডিজিটাল ভান্ডার</title>
    <style>
        body { background-color: #121214; color: #e1e1e6; font-family: 'Georgia', serif; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: auto; background: #18181b; border: 1px solid #27272a; border-radius: 12px; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        h1 { text-align: center; color: #f43f5e; font-family: 'Courier New', monospace; letter-spacing: 2px; margin-bottom: 5px; font-size: 28px; }
        .subtitle { text-align: center; color: #a1a1aa; font-size: 14px; margin-bottom: 25px; font-style: italic; }
        h2 { color: #fb7185; border-bottom: 1px solid #27272a; padding-bottom: 8px; font-size: 20px; }
        .search-box { display: flex; gap: 10px; margin-bottom: 30px; }
        .search-box input { flex: 1; padding: 12px; background: #09090b; border: 1px solid #3f3f46; color: #fafafa; border-radius: 6px; font-size: 14px; }
        .search-box button { background: #f43f5e; color: #fff; border: none; padding: 0 20px; font-weight: bold; cursor: pointer; border-radius: 6px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 6px; font-weight: bold; color: #d4d4d8; font-size: 14px; }
        input[type="text"], input[type="password"], textarea, select, input[type="file"] {
            width: 100%; padding: 10px; background: #09090b; border: 1px solid #3f3f46; color: #fafafa; border-radius: 6px; box-sizing: border-box; font-family: sans-serif;
        }
        .btn-submit { background: #f43f5e; color: #fff; border: none; padding: 12px; width: 100%; font-weight: bold; cursor: pointer; border-radius: 6px; text-transform: uppercase; font-size: 14px; }
        .book-card { background: #09090b; border: 1px solid #27272a; padding: 20px; border-radius: 8px; margin-bottom: 20px; display: flex; gap: 20px; flex-wrap: wrap; }
        .book-cover { width: 120px; height: 160px; object-fit: cover; border-radius: 4px; border: 1px solid #3f3f46; }
        .book-info { flex: 1; }
        .badge { background: #27272a; color: #fb7185; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-family: monospace; }
        .writer-text { font-size: 13px; color: #a1a1aa; margin-top: 4px; font-style: italic; }
        .desc { font-size: 13px; color: #d4d4d8; margin: 8px 0; line-height: 1.4; }
        .caption-box { background: #1f1f23; border-left: 3px solid #f43f5e; padding: 10px; border-radius: 4px; margin: 10px 0; font-size: 13px; font-style: italic; color: #f43f5e; display: flex; justify-content: space-between; align-items: center; }
        .btn-copy { background: #f43f5e; color: #fff; border: none; padding: 4px 8px; border-radius: 4px; font-size: 11px; cursor: pointer; }
        .actions { display: flex; gap: 10px; margin-top: 10px; align-items: center; flex-wrap: wrap; }
        .btn { background: #27272a; color: #f43f5e; border: 1px solid #f43f5e; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 12px; font-weight: bold; cursor: pointer; }
        .comment-box { background: #121214; border: 1px solid #27272a; padding: 8px 10px; border-radius: 6px; margin-top: 8px; font-size: 12px; }
        hr { border: none; border-top: 1px solid #27272a; margin: 25px 0; }
        .admin-nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; background: #09090b; padding: 10px 15px; border-radius: 6px; border: 1px solid #27272a; gap: 10px; flex-wrap: wrap; }
        .admin-nav a { color: #f43f5e; text-decoration: none; font-size: 13px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="admin-nav">
            <span style="font-size: 13px; color: #10b981; font-weight: bold;">📖 বই পড়া ও সার্চ করা সম্পূর্ণ ফ্রি (কোনো পাসওয়ার্ড লাগবে না)</span>
            <div>
                {% if session.get('is_admin') %}
                    <span style="color: #10b981; font-size: 13px; margin-right: 10px;">🟢 আপলোড মোড অন</span>
                    <a href="/logout">লগআউট</a>
                {% else %}
                    <a href="/admin-login">🔐 নতুন বই আপলোড করতে এখানে ক্লিক করুন</a>
                {% endif %}
            </div>
        </div>

        <h1>NISPROHO KOBI SHOMOGRO</h1>
        <div class="subtitle">"কাব্য, উপন্যাস ও সাহিত্যের এক অনন্য ডিজিটাল ভান্ডার"</div>
        
        <form action="/" method="GET" class="search-box">
            <input type="text" name="q" placeholder="বইয়ের নাম বা লেখকের নাম দিয়ে সার্চ করুন..." value="{{ search_query }}">
            <button type="submit">🔍 খুঁজুন</button>
            {% if search_query %}
                <a href="/" style="background: #27272a; color: #fff; padding: 10px 15px; border-radius: 6px; text-decoration: none; font-size: 13px; display: flex; align-items: center;">রিসেট</a>
            {% endif %}
        </form>

        {% if session.get('is_admin') %}
        <hr>
        <h2>নতুন বই বা লেখা আপলোড করুন (Admin Panel)</h2>
        <div style="background: #09090b; padding: 20px; border-radius: 8px; border: 1px solid #27272a; margin-top: 10px;">
            <form action="/upload" method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label>বই বা লেখার নাম (Title):</label>
                    <input type="text" name="title" required>
                </div>
                <div class="form-group">
                    <label>লেখকের নাম (Writer Name):</label>
                    <input type="text" name="writer_name" placeholder="যেমন: নিঃস্ব্রহ কবি" required>
                </div>
                <div class="form-group">
                    <label>বিভাগ (Category):</label>
                    <select name="category">
                        <option value="Uponnash">Uponnash (Novel)</option>
                        <option value="Kobita">Kobita (Poetry)</option>
                        <option value="Golpo">Golpo (Short Story)</option>
                        <option value="Probandho">Probandho (Essay)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>সংক্ষিপ্ত বিবরণ (Description):</label>
                    <textarea name="description" rows="2"></textarea>
                </div>
                <div class="form-group">
                    <label>সেরা লাইন / ক্যাপশন (Shareable Quote):</label>
                    <textarea name="caption" rows="2" placeholder="কবিতা বা উপন্যাসের সেরা লাইন..."></textarea>
                </div>
                <div class="form-group">
                    <label>কভার ছবি (Cover Image - JPG/PNG):</label>
                    <input type="file" name="cover_file" accept=".jpg,.jpeg,.png" required>
                </div>
                <div class="form-group">
                    <label>মূল বইয়ের ফাইল (PDF / TXT):</label>
                    <input type="file" name="book_file" accept=".pdf,.txt" required>
                </div>
                <button type="submit" class="btn-submit">পাবলিশ করুন</button>
            </form>
        </div>
        {% endif %}

        <hr>
        <h2>প্রকাশিত রচনাবলী (স্ক্রোল করে পড়ুন)</h2>
        <div>
            {% if books %}
                {% for book in books %}
                    <div class="book-card">
                        <img src="/static/uploads/{{ book[7] }}" class="book-cover" alt="Cover">
                        <div class="book-info">
                            <span class="badge">{{ book[3] }}</span>
                            <h3 style="margin: 6px 0 2px 0; color: #fff;">{{ book[1] }}</h3>
                            <div class="writer-text">লেখক: <b>{{ book[2] }}</b></div>
                            <p class="desc">{{ book[4] }}</p>
                            
                            {% if book[5] %}
                                <div class="caption-box">
                                    <span id="caption-{{ book[0] }}">"{{ book[5] }}"</span>
                                    <button class="btn-copy" onclick="copyCaption('caption-{{ book[0] }}')">📋 কপি</button>
                                </div>
                            {% endif %}
                            
                            <div class="actions">
                                <a class="btn" href="/static/uploads/{{ book[6] }}" target="_blank">📖 পড়ুন / ডাউনলোড</a>
                                <a class="btn" href="/like/{{ book[0] }}">❤️ রিঅ্যাক্ট ({{ book[8] }})</a>
                                <button class="btn" onclick="saveBookmark('{{ book[1] }}')">🔖 বুকমার্ক</button>
                            </div>

                            <div style="margin-top: 15px;">
                                <strong style="font-size: 13px; color: #fb7185;">পাঠকের মন্তব্য:</strong>
                                {% for comment in comments %}
                                    {% if comment[1] == book[0] %}
                                        <div class="comment-box">
                                            <b>{{ comment[2] }}:</b> {{ comment[3] }}
                                        </div>
                                    {% endif %}
                                {% endfor %}

                                <form action="/comment/{{ book[0] }}" method="POST" style="margin-top: 8px; display: flex; gap: 5px;">
                                    <input type="text" name="user_name" placeholder="আপনার নাম..." required style="width: 30%; font-size: 11px; padding: 5px;">
                                    <input type="text" name="comment_text" placeholder="মন্তব্য করুন..." required style="font-size: 11px; padding: 5px;">
                                    <button type="submit" style="width: auto; padding: 5px 12px; font-size: 11px; background:#f43f5e; color:#fff; border:none; border-radius:4px; cursor:pointer;">পোস্ট</button>
                                </form>
                            </div>
                        </div>
                    </div>
                {% endfor %}
            {% else %}
                <p style="text-align: center; color: #71717a; font-style: italic;">কোনো বই বা লেখা পাওয়া যায়নি।</p>
            {% endif %}
        </div>
    </div>
    <script>
        function copyCaption(elementId) {
            let text = document.getElementById(elementId).innerText;
            navigator.clipboard.writeText(text).then(function() { alert('ক্যাপশন সফলভাবে কপি করা হয়েছে!'); });
        }
        function saveBookmark(bookTitle) {
            localStorage.setItem('nisproho_bookmark', bookTitle);
            alert('বুকমার্ক সেভ করা হয়েছে: ' + bookTitle);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if search_query:
        cursor.execute("SELECT * FROM publications WHERE title LIKE ? OR writer_name LIKE ? ORDER BY id DESC", ('%' + search_query + '%', '%' + search_query + '%'))
    else:
        cursor.execute('SELECT * FROM publications ORDER BY id DESC')
    books = cursor.fetchall()
    cursor.execute('SELECT * FROM comments')
    comments = cursor.fetchall()
    conn.close()
    return render_template_string(WEB_TEMPLATE, books=books, comments=comments, search_query=search_query)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'Writer-pro@admin':
            session['is_admin'] = True
            return redirect(url_for('index'))
        return "<script>alert('ভুল পাসওয়ার্ড!'); window.location='/admin-login';</script>"
    return """
    <body style="background:#121214; color:#fff; font-family:sans-serif; text-align:center; padding-top:20vh;">
        <form method="POST" style="display:inline-block; border:1px solid #27272a; background:#18181b; padding:30px; border-radius:12px; width:300px;">
            <h3 style="color:#f43f5e; margin-top:0;">🔒 আপলোড অথেন্টিকেশন</h3>
            <p style="font-size:12px; color:#a1a1aa; margin-bottom:20px;">নতুন বই আপলোড করতে কমন পাসওয়ার্ড দিন।</p>
            <input type="password" name="password" placeholder="Admin Password" required style="padding:10px; width:100%; box-sizing:border-box; background:#09090b; border:1px solid #3f3f46; color:#fff; border-radius:6px; margin-bottom:15px;"><br>
            <button type="submit" style="padding:10px; width:100%; background:#f43f5e; color:#fff; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">লগইন করুন</button>
            <br><br>
            <a href="/" style="color:#a1a1aa; font-size:12px; text-decoration:none;">← হোমপেজে ফিরে যান</a>
        </form>
    </body>
    """

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    title = request.form.get('title')
    writer_name = request.form.get('writer_name')
    category = request.form.get('category')
    description = request.form.get('description')
    caption = request.form.get('caption')
    cover_file = request.files.get('cover_file')
    book_file = request.files.get('book_file')
    
    if cover_file and book_file:
        cover_name = cover_file.filename
        book_name = book_file.filename
        cover_file.save(os.path.join(UPLOAD_FOLDER, cover_name))
        book_file.save(os.path.join(UPLOAD_FOLDER, book_name))
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO publications (title, writer_name, category, description, caption, filename, cover_image, likes) VALUES (?, ?, ?, ?, ?, ?, ?, 0)', (title, writer_name, category, description, caption, book_name, cover_name))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/like/<int:book_id>')
def like_book(book_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE publications SET likes = likes + 1 WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/comment/<int:book_id>', methods=['POST'])
def add_comment(book_id):
    user_name = request.form.get('user_name')
    comment_text = request.form.get('comment_text')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO comments (book_id, user_name, comment) VALUES (?, ?, ?)', (book_id, user_name, comment_text))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

