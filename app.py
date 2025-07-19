from flask import Flask, render_template, request, redirect
from helper import preprocessing, vectorizer, get_prediction
from logger import logging

app = Flask(__name__)

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


@app.route('/how-it-works')
def how_it_works():
    return render_template('howitworks.html')


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
