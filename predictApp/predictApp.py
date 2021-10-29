import pandas as pd
import en_core_web_sm
from utils.utils import data_preprocessing_predict
import pickle
import numpy as np


class PredictApi:

    def __init__(self, stopWords_file_path):

        self.nlp = en_core_web_sm.load()
        self.stopWords_file_path = stopWords_file_path
        self.target_classes = ['Negative', 'Positive']

    def execute_processing(self, text, model_path, vector_path):

        df = pd.DataFrame([text], columns=['text'])
        print(df['text'])
        df['text'] = data_preprocessing_predict(df['text'], self.stopWords_file_path)
        # loading models
        with open(vector_path, 'rb') as f:
            TfidfVect = pickle.load(f)
        with open(model_path, 'rb') as f:
            svm_model = pickle.load(f)

        pred_vect = TfidfVect.transform(df['text'][0])
        prediction = svm_model.predict(pred_vect)
        prediction_probability = svm_model.predict_proba(pred_vect)

        if list(prediction_probability.flatten())[0] == list(prediction_probability.flatten())[1]:
            return "UnKnown"
        elif list(prediction_probability.flatten())[np.argmax(prediction_probability)] > 0.5:
            return prediction
        else:
            return "UnKnown"
