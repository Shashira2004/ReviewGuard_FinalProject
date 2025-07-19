from flask import Flask, render_template, request, redirect 
from helper import preprocessing, vectorizer, get_prediction

app = Flask(__name__)

data = dict()
reviews = []
real = 0
fake = 0

@app.route('/')
def index():
    data['reviews'] = reviews
    data['real'] = real
    data['fake'] = fake
    return render_template('index.html', data=data)

@app.route('/', methods=['post'])
def my_post():
    text = request.form['text']
    preprocessed_txt = preprocessing(text)
    vectorized_txt = vectorizer(preprocessed_txt)
    prediction = get_prediction(vectorized_txt)

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
