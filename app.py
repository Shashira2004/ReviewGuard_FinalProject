from flask import Flask, render_template, request, redirect, url_for, session, send_file
from helper import preprocessing, vectorizer, get_prediction
from logger import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
from flask import make_response



import firebase_admin
from firebase_admin import auth, credentials

# Only do this once globally
cred = credentials.Certificate("artifacts/reviewguard-310f6-firebase-adminsdk-fbsvc-7d1e2ee5d6.json")
firebase_admin.initialize_app(cred)

app = Flask(__name__)

import os
app.secret_key = os.urandom(24)


logging.info('Flask server started...')

data = dict()
reviews = []
real = 0
fake = 0

# ✅ Serve the new homepage
@app.route('/')
def home():
    logging.info('===== Open Home Page =====')
    return render_template('home.html')  # <-- Make sure this file exists

# ✅ Serve the review checker page
@app.route('/index')
def index():
    data['reviews'] = reviews
    data['real'] = real
    data['fake'] = fake

    logging.info('===== Open Review Page =====')
    return render_template('index.html', data=data)

@app.route('/register')
def register():
    return render_template('register.html')  # signup page

@app.route('/login')
def login():
    return render_template('login.html')  # signin page

@app.route('/login', methods=['POST'])
def firebase_login():
    id_token = request.form['idToken']
    decoded_token = auth.verify_id_token(id_token)
    uid = decoded_token['uid']
    session['uid'] = uid

    user = auth.get_user(uid)
    is_admin = user.custom_claims.get('admin') if user.custom_claims else False
    session['is_admin'] = is_admin

    if is_admin:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))  # or whatever your home route is


@app.route('/how-it-works')
def how_it_works():
    return render_template('howitworks.html')

@app.route('/about')
def about():
    return render_template('aboutus.html')

@app.route('/contact')
def contact():
    return render_template('contactus.html')

# @app.route('/admin')
# def admin_dashboard():
#     if 'user' in session:
#         id_token = session['user']['idToken']
#         decoded_token = auth.verify_id_token(id_token)
#         if decoded_token.get('admin'):
#             return render_template('admin.html')
#         else:
#             return "Access Denied", 403
#     return redirect(url_for('login'))


@app.route('/admin', methods=['GET'])
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('home'))

    # Fetch users from Firebase
    all_users = []
    page = auth.list_users()
    while page:
        for user in page.users:
            is_admin = user.custom_claims.get('admin') if user.custom_claims else False
            all_users.append({
                'uid': user.uid,
                'email': user.email,
                'admin': is_admin
            })
        page = page.get_next_page()
    
    return render_template('admin.html', users=all_users)

@app.route('/make-admin', methods=['POST'])
def make_admin():
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    uid = request.form['uid']
    auth.set_custom_user_claims(uid, {'admin': True})
    return redirect(url_for('admin_dashboard'))

@app.route('/delete-user', methods=['POST'])
def delete_user():
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    uid = request.form['uid']
    auth.delete_user(uid)
    return redirect(url_for('admin_dashboard'))

def get_all_users():
    users = []
    page = auth.list_users()
    while page:
        for user in page.users:
            users.append({
                'email': user.email,
                'uid': user.uid,
                'admin': user.custom_claims.get('admin', False) if user.custom_claims else False
            })
        page = page.get_next_page()
    return users


@app.route('/export_users_pdf')
def export_users_pdf():
    from io import BytesIO
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    title = Paragraph("<b>Review Guard User Details</b>", styles['Title'])
    spacer = Spacer(1, 0.25 * inch)

    users = get_all_users()
    data = [['Email', 'UID', 'Admin']] + [
        [user['email'], user['uid'], 'Yes' if user['admin'] else 'No'] for user in users
    ]

    table = Table(data, colWidths=[2.5*inch, 2.5*inch, 1*inch])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)

    elements = [title, spacer, table]
    doc.build(elements)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="user_report.pdf", mimetype='application/pdf')

@app.route('/profile')
def profile():
    return render_template('profile.html')


# ✅ Handle review form POST on /index
@app.route('/index', methods=['POST'])
def handle_post():
    text = request.form['text']
    logging.info(f'Text : {text}')

    preprocessed_txt = preprocessing(text)
    logging.info(f'Preprocessed Text : {preprocessed_txt}')

    vectorized_txt = vectorizer(preprocessed_txt)
    logging.info(f'Vectorized Text : {vectorized_txt}')

    prediction = get_prediction(vectorized_txt)
    logging.info(f'Prediction : {prediction}')

    global real, fake
    if prediction == 'fake':
        fake += 1
    else:
        real += 1

    reviews.insert(0, text)
    return redirect('/index')  # redirect back to review page after POST

if __name__ == '__main__':
    app.run()









# from flask import Flask, render_template, request, redirect 
# from helper import preprocessing, vectorizer, get_prediction
# from logger import logging

# app = Flask(__name__)

# logging.info('Flask server started...')

# data = dict()
# reviews = []
# real = 0
# fake = 0

# @app.route('/')
# def index():
#     data['reviews'] = reviews
#     data['real'] = real
#     data['fake'] = fake

#     logging.info('===== Open home page =====')

#     return render_template('index.html', data=data)

# @app.route('/', methods=['post'])
# def my_post():
#     text = request.form['text']
#     logging.info(f'Text : {text}')

#     preprocessed_txt = preprocessing(text)
#     logging.info(f'Preprocessed Text : {preprocessed_txt}')

#     vectorized_txt = vectorizer(preprocessed_txt)
#     logging.info(f'Vectorized Text : {vectorized_txt}')

#     prediction = get_prediction(vectorized_txt)
#     logging.info(f'Prediction : {prediction}')

#     if prediction == 'fake':
#         global fake
#         fake += 1
#     else:
#         global real
#         real += 1

#     reviews.insert(0, text)
#     return redirect(request.url) 


# if __name__ == '__main__':
#     app.run()
