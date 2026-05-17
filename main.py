from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session, flash
from cryptography.fernet import Fernet
import base64
import secrets
import yagmail
app = Flask(__name__)
app.secret_key = 'stego_secret_key'
SENDER_EMAIL = "mohan1204p@gmail.com"
SENDER_PASSWORD = "egiytgqxooehtanr"

# --- 1. DATABASE CONNECTION ---
def get_db_connection():
    conn = sqlite3.connect('database.db', detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gender TEXT,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shared_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            file_name TEXT,
            ecc_key TEXT,
            lsb_key TEXT,
            status TEXT DEFAULT 'Sent',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            secret_text TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Ensure upload folders exist (runs on startup)
if not os.path.exists('static/uploads/originals'):
    os.makedirs('static/uploads/originals')
if not os.path.exists('static/uploads/encrypted'):
    os.makedirs('static/uploads/encrypted')

# Initialize DB on startup
with app.app_context():
    init_db()

# --- 2. CORE LOGIC PLACEHOLDERS (Your Algorithms) ---
def lsb_encode(image_path, secret_text, key):
    # Combine key and text with EOF marker
    data = f"{key}:{secret_text}"
    binary_data = ''.join(format(ord(i), '08b') for i in data) + '1111111111111110'

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image reading failed. Check the file path.")

    # Convert image to 1D array for faster bit manipulation
    flattened = img.flatten()

    if len(binary_data) > len(flattened):
        raise ValueError("Secret text is too long for this image size!")

    # Applying the bitmask safely
    for i in range(len(binary_data)):
        # 254 ensures the LSB is cleared (set to 0) without overflow
        flattened[i] = (flattened[i] & 254) | int(binary_data[i])

    # Reshape back to original image dimensions
    stego_img = flattened.reshape(img.shape)

    base_name = os.path.splitext(os.path.basename(image_path))[0]
    stego_filename = "stego_" + base_name + ".png"
    stego_path = os.path.join('static/uploads/originals', stego_filename)
    cv2.imwrite(stego_path, stego_img)
    return stego_path, stego_filename


def split_and_encrypt(stego_path, ecc_key):
    img = cv2.imread(stego_path)
    h, w, _ = img.shape

    # 2x2 Matrix Splitting
    mid_h, mid_w = h // 2, w // 2
    puzzles = [
        img[0:mid_h, 0:mid_w],  # Top-Left
        img[0:mid_h, mid_w:w],  # Top-Right
        img[mid_h:h, 0:mid_w],  # Bottom-Left
        img[mid_h:h, mid_w:w]  # Bottom-Right
    ]

    # ECC Key setup - Ensuring exactly 32 bytes for Fernet
    padded_key = base64.urlsafe_b64encode(ecc_key.ljust(32)[:32].encode())
    fernet = Fernet(padded_key)

    encrypted_paths = []
    for i, part in enumerate(puzzles):
        # Encode piece as PNG bytes before encryption
        _, buffer = cv2.imencode('.png', part)
        encrypted_data = fernet.encrypt(buffer.tobytes())

        enc_filename = f"puzzle_{i}_{os.path.basename(stego_path)}.enc"
        enc_path = os.path.join('static/uploads/encrypted', enc_filename)

        with open(enc_path, 'wb') as f:
            f.write(encrypted_data)
        encrypted_paths.append(enc_filename)

    return encrypted_paths


# --- 3. FLASK ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # HTML form-la irunthu ella data-vum collect pandrom
        name = request.form.get('name')
        gender = request.form.get('gender')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        uname = request.form.get('uname')  # HTML-la 'uname' nu kuduthurukom
        password = request.form.get('password')

        db = get_db_connection()
        cursor = db.cursor()
        try:
            # MySQL database-la insert pandrom
            sql = """INSERT INTO users 
                     (name, gender, email, phone, address, username, password) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)"""

            cursor.execute(sql, (name, gender, email, phone, address, uname, password))
            db.commit()

            flash("Registration Success! Please Login.")
            return redirect(url_for('login'))

        except Exception as e:
            # Error vantha flash message kaatum
            flash(f"Error: {e}")
            db.rollback()  # Database error vantha changes-a cancel pannanum

        finally:
            cursor.close()
            db.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        db.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('userhome'))
        else:
            flash("Invalid email or password")

    return render_template('login.html')


@app.route('/userhome')
def userhome():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    uid = session['user_id']
    db = get_db_connection()
    cursor = db.cursor()

    # 1. Stats
    cursor.execute("SELECT COUNT(*) as count FROM shared_files WHERE sender_id = ?", (uid,))
    total_sent = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM shared_files WHERE receiver_id = ?", (uid,))
    total_received = cursor.fetchone()['count']

    # 2. Combined Recent Transactions (Timeline)
    # Using a UNION to show both sent and received in one list
    cursor.execute("""
        SELECT f.*, u.name as partner_name FROM shared_files f 
        JOIN users u ON f.receiver_id = u.id WHERE f.sender_id = ?
        UNION
        SELECT f.*, u.name as partner_name FROM shared_files f 
        JOIN users u ON f.sender_id = u.id WHERE f.receiver_id = ?
        ORDER BY created_at DESC LIMIT 8
    """, (uid, uid))
    recent_files = cursor.fetchall()

    db.close()
    return render_template('userhome.html',
                           total_sent=total_sent,
                           total_received=total_received,
                           recent_files=recent_files)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # 1. Database Connection open pandrom
    db = get_db_connection()
    cursor = db.cursor()

    if request.method == 'POST':
        receiver_id = request.form.get('receiver_id')
        secret_text = request.form.get('secret_text')
        cover_img = request.files.get('cover_image')

        # Generate secure keys automatically
        lsb_key = secrets.token_hex(8)
        ecc_key = secrets.token_hex(8)

        if cover_img:
            filename = cover_img.filename
            temp_path = os.path.join('static/uploads/originals', 'temp_' + filename)
            cover_img.save(temp_path)

            try:
                # A. LSB Encoding
                stego_path, stego_filename = lsb_encode(temp_path, secret_text, lsb_key)

                # B. Split & Encrypt
                split_and_encrypt(stego_path, ecc_key)

                # C. Get receiver details
                cursor.execute("SELECT email, name FROM users WHERE id = ?", (receiver_id,))
                receiver_data = cursor.fetchone()

                # D. Insert into Database
                sql = """INSERT INTO shared_files 
                         (sender_id, receiver_id, file_name, lsb_key, ecc_key, status,secret_text) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)"""
                cursor.execute(sql, (session['user_id'], receiver_id, stego_filename, lsb_key, ecc_key, 'Sent',secret_text))
                db.commit()

                # E. Send Email via Yagmail
                try:
                    yag = yagmail.SMTP(SENDER_EMAIL, SENDER_PASSWORD)
                    yag.send(
                        to=receiver_data['email'],
                        subject="Secure File Received - Decryption Keys",
                        contents=[
                            f"Hi {receiver_data['name']},",
                            f"User {session['username']} has sent you a secure file.",
                            f"1. ECC Key (Image Reconstruction): {ecc_key}",
                            f"2. LSB Key (Text Extraction): {lsb_key}"
                        ]
                    )
                    email_status = "Keys sent to email."
                except Exception as mail_err:
                    email_status = f"Warning: File processed but email failed: {mail_err}"

                os.remove(temp_path)
                db.close()  # Close before redirecting
                flash(f"Success! {email_status}")
                return redirect(url_for('userhome'))

            except Exception as e:
                db.rollback()
                flash(f"Error in processing: {str(e)}")

    # 2. Intha part GET request-kum work aagum, POST fail aana thirumba form-kum pogum
    cursor.execute("SELECT id, name, email FROM users WHERE id != ?", (session['user_id'],))
    all_users = cursor.fetchall()

    db.close()  # Connection-a final-a close pandrom
    return render_template('upload.html', all_users=all_users)


@app.route('/receiving')
def receiving():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    # Intha user-ku yaralam file anupirukangalo athai mattum fetch pandrom
    cursor.execute("""
        SELECT f.*, u.name as sender_name 
        FROM shared_files f 
        JOIN users u ON f.sender_id = u.id 
        WHERE f.receiver_id = ? 
        ORDER BY f.created_at DESC
    """, (session['user_id'],))

    received_files = cursor.fetchall()
    db.close()

    return render_template('receiving.html', files=received_files)


def decrypt_and_merge(file_name, ecc_key):
    # Setup Fernet with the provided key
    padded_key = base64.urlsafe_b64encode(ecc_key.ljust(32)[:32].encode())
    fernet = Fernet(padded_key)

    puzzles = []
    for i in range(4):
        enc_path = os.path.join('static/uploads/encrypted', f"puzzle_{i}_{file_name}.enc")

        with open(enc_path, 'rb') as f:
            encrypted_data = f.read()

        # Decrypt puzzle data
        decrypted_data = fernet.decrypt(encrypted_data)

        # Convert bytes back to OpenCV image
        nparr = np.frombuffer(decrypted_data, np.uint8)
        part = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        puzzles.append(part)

    # Reconstruct the 2x2 grid
    top_row = np.hstack((puzzles[0], puzzles[1]))
    bottom_row = np.hstack((puzzles[2], puzzles[3]))
    reconstructed_img = np.vstack((top_row, bottom_row))

    return reconstructed_img


def lsb_decode_text(img, lsb_key):
    try:
        flattened = img.flatten()
        binary_data = ""

        # 1. Extract bits
        for i in range(len(flattened)):
            binary_data += str(flattened[i] & 1)
            # Optimization: Stop if we find the 16-bit EOF marker
            if len(binary_data) > 16 and binary_data[-16:] == '1111111111111110':
                break

        # 2. Convert binary string to actual characters
        all_bytes = [binary_data[i:i + 8] for i in range(0, len(binary_data) - 16, 8)]
        decoded_str = ""
        for b in all_bytes:
            decoded_str += chr(int(b, 2))

        print(f"Decoded raw string: {decoded_str}")  # For debugging in console

        # 3. Validation
        if ":" in decoded_str:
            # We use partition to avoid issues if the secret text contains ":"
            stored_key, _, message = decoded_str.partition(":")
            if stored_key == lsb_key:
                return message
            else:
                print(f"Key Mismatch: Input={lsb_key}, Found={stored_key}")

        return None
    except Exception as e:
        print(f"LSB Decode Error: {e}")
        return None

@app.route('/decrypt_view/<int:file_id>', methods=['GET', 'POST'])
def decrypt_view(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "SELECT f.*, u.username as sender_name FROM shared_files f JOIN users u ON f.sender_id = u.id WHERE f.id = ?",
        (file_id,))
    file_data = cursor.fetchone()

    secret_message = None
    reconstructed_image_path = None

    if request.method == 'POST':
        input_ecc = request.form.get('ecc_key')
        input_lsb = request.form.get('lsb_key')

        try:
            # Step 1: ECC Verification & Puzzle Merging
            # Inga logic merge aagi image object-a return pannum
            text=file_data['secret_text']
            reconstructed_img = decrypt_and_merge(file_data['file_name'], input_ecc)

            # Step 2: Temporary-a reconstructed image-a save pandrom (view pannurathukaga)
            view_filename = f"view_{file_data['file_name']}"
            view_path = os.path.join('static/uploads/originals', view_filename)
            cv2.imwrite(view_path, reconstructed_img)
            reconstructed_image_path = view_filename  # HTML-ku anupa

            # Step 3: LSB Verification
            extracted_text = lsb_decode_text(reconstructed_img, input_lsb)

            if extracted_text:
                secret_message = text
                flash("Key Verification Successful!", "success")
            else:
                secret_message = None
                reconstructed_image_path = None
                flash("Invalid LSB Key! Text extraction failed.", "danger")

        except Exception as e:
            flash("Invalid ECC Key! Image reconstruction failed.", "danger")

    db.close()
    return render_template('decrypt_view.html', file=file_data,
                           secret_message=secret_message,
                           reconstructed_image=reconstructed_image_path)


@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    uid = session['user_id']
    db = get_db_connection()
    cursor = db.cursor()

    # Fetching all transactions where user is either sender or receiver
    cursor.execute("""
        SELECT f.*, 
               u1.name as sender_name, 
               u2.name as receiver_name 
        FROM shared_files f
        JOIN users u1 ON f.sender_id = u1.id
        JOIN users u2 ON f.receiver_id = u2.id
        WHERE f.sender_id = ? OR f.receiver_id = ?
        ORDER BY f.created_at DESC
    """, (uid, uid))

    all_reports = cursor.fetchall()
    db.close()

    return render_template('reports.html', reports=all_reports)


@app.route('/view/<int:file_id>')
def view_transaction(file_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    cursor = db.cursor()

    # Fetching file and sender/receiver details
    cursor.execute("""
        SELECT f.*, 
               u1.name as sender_name, 
               u2.name as receiver_name 
        FROM shared_files f
        JOIN users u1 ON f.sender_id = u1.id
        JOIN users u2 ON f.receiver_id = u2.id
        WHERE f.id = ? AND (f.sender_id = ? OR f.receiver_id = ?)
    """, (file_id, session['user_id'], session['user_id']))

    file_data = cursor.fetchone()
    db.close()

    if not file_data:
        flash("Unauthorized access or file not found.")
        return redirect(url_for('userhome'))

    return render_template('view_file.html', file=file_data)
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)