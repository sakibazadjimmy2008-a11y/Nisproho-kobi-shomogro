import os
import json
from datetime import datetime
from flask import (
    Flask, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash, 
    jsonify, 
    abort
)
from werkzeug.utils import secure_filename

# ==========================================
# 1. APPLICATION INITIALIZATION & CONFIG
# ==========================================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'nispriho_pro_secure_master_key_2026')

# Directory & Storage Paths
UPLOAD_FOLDER = os.path.join('static', 'uploads')
DATA_DIR = os.path.join('data')
DATABASE_FILE = os.path.join(DATA_DIR, 'library_database.json')

ALLOWED_BOOK_EXTENSIONS = {'pdf', 'epub'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Max 50MB upload limit

# Ensure required directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Admin Upload Password Specification
ADMIN_UPLOAD_PASSWORD = "Writer-pro@admin"
SITE_NAME = "Nispriho Kobi Shomogro"


# ==========================================
# 2. DATABASE UTILITIES (JSON PERSISTENCE)
# ==========================================
def load_database():
    """Loads the core book repository from persistent JSON storage."""
    if not os.path.exists(DATABASE_FILE):
        save_database([])
        return []
    try:
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                return []
            return json.loads(content)
    except Exception as e:
        print(f"[Database Error] Failed to load records: {e}")
        return []

def save_database(books):
    """Commits state changes safely to the persistent JSON store."""
    try:
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(books, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[Database Error] Failed to write records: {e}")


# ==========================================
# 3. HELPER FUNCTIONS & VALIDATORS
# ==========================================
def allowed_file(filename, allowed_extensions):
    """Validates uploaded file extensions against security policies."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def sanitize_metadata(text):
    """Basic text sanitization for user inputs."""
    if not text:
        return ""
    return text.strip()


# ==========================================
# 4. CORE ROUTING & CONTROLLERS
# ==========================================

@app.route('/')
def index():
    """Main library index featuring search, category filters, and grid rendering."""
    query = sanitize_metadata(request.args.get('search', ''))
    category = sanitize_metadata(request.args.get('category', 'All'))
    
    books = load_database()
    filtered_books = books
    
    # Advanced Search Engine (Title & Author Matching)
    if query:
        filtered_books = [
            b for b in filtered_books 
            if query.lower() in b['title'].lower() or query.lower() in b['writer'].lower()
        ]
        
    # Categorization Filter (Kobita, Golpo, Uponnash, etc.)
    if category and category != 'All':
        filtered_books = [b for b in filtered_books if b['category'] == category]
        
    # Sort books by recent uploads first
    filtered_books = sorted(filtered_books, key=lambda x: x.get('id', 0), reverse=True)
    
    return render_template(
        'index.html', 
        books=filtered_books, 
        site_name=SITE_NAME, 
        query=query, 
        current_category=category,
        total_books=len(books)
    )


@app.route('/upload', methods=['GET', 'POST'])
def upload_book():
    """Secure administrative upload portal for publishing literary works."""
    if request.method == 'POST':
        password = request.form.get('password', '')
        title = sanitize_metadata(request.form.get('title'))
        writer = sanitize_metadata(request.form.get('writer'))
        category = sanitize_metadata(request.form.get('category'))
        description = sanitize_metadata(request.form.get('description', ''))
        
        # Security Gate: Password Validation
        if password != ADMIN_UPLOAD_PASSWORD:
            flash('প্রবেশাধিকার সংরক্ষিত: ভুল আপলোড পাসওয়ার্ড দেওয়া হয়েছে!', 'danger')
            return redirect(url_for('upload_book'))
        
        # Validate Form Inputs
        if not title or not writer or not category:
            flash('অনুগ্রহ করে সকল আবশ্যক তথ্য পূরণ করুন!', 'warning')
            return redirect(url_for('upload_book'))
            
        # Validate File Handlers
        if 'file' not in request.files or 'cover' not in request.files:
            flash('বইয়ের ফাইল অথবা কভার ছবি সংযুক্ত করা হয়নি!', 'warning')
            return redirect(url_for('upload_book'))
            
        book_file = request.files['file']
        cover_file = request.files['cover']
        
        if book_file.filename == '' or cover_file.filename == '':
            flash('ফাইল নির্বাচন প্রক্রিয়া অসম্পূর্ণ রয়েছে!', 'warning')
            return redirect(url_for('upload_book'))
            
        # Process Validated Files
        if book_file and allowed_file(book_file.filename, ALLOWED_BOOK_EXTENSIONS) and \
           cover_file and allowed_file(cover_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            
            try:
                book_filename = secure_filename(f"{datetime.now().timestamp()}_{book_file.filename}")
                cover_filename = secure_filename(f"{datetime.now().timestamp()}_{cover_file.filename}")
                
                book_path = os.path.join(app.config['UPLOAD_FOLDER'], book_filename)
                cover_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_filename)
                
                book_file.save(book_path)
                cover_file.save(cover_path)
                
                # Load DB, append new entry, persist changes
                books = load_database()
                new_id = (max([b['id'] for b in books]) + 1) if books else 1
                
                new_book_record = {
                    'id': new_id,
                    'title': title,
                    'writer': writer,
                    'category': category,
                    'description': description,
                    'file_url': url_for('static', filename=f'uploads/{book_filename}'),
                    'cover_url': url_for('static', filename=f'uploads/{cover_filename}'),
                    'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'likes': 0,
                    'comments': []
                }
                
                books.append(new_book_record)
                save_database(books)
                
                flash('অভিনন্দন! সাহিত্যকর্মটি সফলভাবে লাইব্রেরিতে প্রকাশিত হয়েছে।', 'success')
                return redirect(url_for('index'))
                
            except Exception as e:
                flash(f'সার্ভার ত্রুটি: ফাইল সংরক্ষণ ব্যর্থ হয়েছে - {str(e)}', 'danger')
                return redirect(url_for('upload_book'))
        else:
            flash('অবৈধ ফাইল ফরম্যাট! শুধুমাত্র PDF/EPUB এবং সঠিক ইমেজ ফরম্যাট অনুমোদিত।', 'danger')
            return redirect(url_for('upload_book'))
            
    return render_template('upload.html', site_name=SITE_NAME)


@app.route('/read/<int:book_id>', methods=['GET', 'POST'])
def read_book(book_id):
    """Reading room layout supporting live interaction, metrics, and reviews."""
    books = load_database()
    target_book = None
    target_index = -1
    
    for idx, b in enumerate(books):
        if b['id'] == book_id:
            target_book = b
            target_index = idx
            break
            
    if not target_book:
        flash('কাঙ্ক্ষিত সাহিত্যকর্মটি লাইব্রেরিতে খুঁজে পাওয়া যায়নি!', 'danger')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'like':
            target_book['likes'] += 1
            save_database(books)
            return redirect(url_for('read_book', book_id=book_id))
            
        elif action == 'comment':
            commenter_name = sanitize_metadata(request.form.get('commenter_name', 'অজ্ঞাত পাঠক'))
            comment_text = sanitize_metadata(request.form.get('comment_text'))
            
            if comment_text:
                comment_entry = {
                    'name': commenter_name if commenter_name else 'অজ্ঞাত পাঠক',
                    'text': comment_text,
                    'time': datetime.now().strftime("%d %b %Y, %I:%M %p")
                }
                target_book['comments'].append(comment_entry)
                save_database(books)
                flash('আপনার মতামত সফলভাবে যুক্ত হয়েছে।', 'success')
            else:
                flash('শূন্য মতামত পোস্ট করা সম্ভব নয়।', 'warning')
                
            return redirect(url_for('read_book', book_id=book_id))
            
    return render_template('read.html', book=target_book, site_name=SITE_NAME)


# ==========================================
# 5. ERROR HANDLERS & API ENDPOINTS
# ==========================================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', site_name=SITE_NAME), 404

@app.errorhandler(500)
def internal_server_error(e):
    return "<h3>৫০০ ইন্টারনাল সার্ভার ত্রুটি: সিস্টেম অ্যাডমিনিস্ট্রেটরের সাথে যোগাযোগ করুন।</h3>", 500


# ==========================================
# 6. APPLICATION EXECUTION ENTRY POINT
# ==========================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
