from flask import Flask, render_template, request, redirect 
from helper import preprocessing, vectorizer, get_prediction
from logger import logging

app = Flask(__name__)

logging.info('Flask server started...')

data = dict()
reviews = []
real = 0
fake = 0

@app.route('/')
def index():
    data['reviews'] = reviews
    data['real'] = real
    data['fake'] = fake

    logging.info('===== Open home page =====')

    return render_template('index.html', data=data)

@app.route('/', methods=['post'])
def my_post():
    text = request.form['text']
    logging.info(f'Text : {text}')

    preprocessed_txt = preprocessing(text)
    logging.info(f'Preprocessed Text : {preprocessed_txt}')

    vectorized_txt = vectorizer(preprocessed_txt)
    logging.info(f'Vectorized Text : {vectorized_txt}')

    prediction = get_prediction(vectorized_txt)
    logging.info(f'Prediction : {prediction}')

    if prediction == 'fake':
        global fake
        fake += 1
    else:
        global real
        real += 1

    reviews.insert(0, text)
    return redirect(request.url) 


if __name__ == '__main__':
    app.run()
