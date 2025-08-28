import numpy as np
import pandas as pd
import re
import string
import pickle

from nltk.stem import PorterStemmer
ps = PorterStemmer()

# load model
with open('static/model/model.pickle', 'rb') as f:
    model = pickle.load(f)

# load stopwords
with open('static/model/corpora/stopwords/english', 'r') as file:
    sw = file.read().splitlines()

# load tokens
vocab = pd.read_csv('static/model/vocabulary.txt', header=None)
tokens = vocab[0].tolist()


def remove_punctuations(text):
    for punctuation in string.punctuation:
        text = text.replace(punctuation, '')
    return text

def preprocessing(text):
    data = pd.DataFrame([text], columns=['review'])
    data["review"] = data["review"].apply(lambda x: " ".join(x.lower() for x in x.split()))
    data["review"] = data['review'].apply(lambda x: " ".join(re.sub(r'^https?:\/\/.*[\r\n]*', '', x, flags=re.MULTILINE) for x in x.split()))
    data["review"] = data["review"].apply(remove_punctuations)
    data["review"] = data['review'].str.replace(r'\d+', '', regex=True)
    data["review"] = data["review"].apply(lambda x: " ".join(x for x in x.split() if x not in sw))
    data["review"] = data["review"].apply(lambda x: " ".join(ps.stem(x) for x in x.split()))
    return data["review"]

def vectorizer(ds):
    vectorized_lst = []
    for sentence in ds:
        sentence_lst = np.zeros(len(tokens))
        for i in range(len(tokens)):
            if tokens[i] in sentence.split():
                sentence_lst[i] = 1 
        vectorized_lst.append(sentence_lst)
    vectorized_lst_new = np.asarray(vectorized_lst, dtype=np.float32)
    return vectorized_lst_new

def get_prediction(vectorized_text):
    prediction = model.predict(vectorized_text)
    if prediction == 1:
        return 'fake'
    else:
        return 'real'
    
def get_prediction_prob(vectorized_text):
    # Assuming binary classification: 0 = real, 1 = fake
    probs = model.predict_proba(vectorized_text)[0]  # returns [prob_real, prob_fake]
    real_prob = probs[0] * 100  # convert to percentage
    fake_prob = probs[1] * 100
    # Determine the predicted class as well
    pred_class = 'fake' if fake_prob > real_prob else 'real'
    return pred_class, real_prob, fake_prob

