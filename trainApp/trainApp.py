import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import naive_bayes
from utils.utils import preprocess_training_data


# remind at last to save the log directly under the directory where we are storing the data

class TrainApi:

    def __init__(self, stopWords_filePath, ):

        self.stopWords = stopWords_filePath


    def training_model(self, json_file_path, modelPath, searchString):

        df = preprocess_training_data(json_file_path, self.stopWords)

        # train set and prediction set
        x = df['text']
        y = df['target']
        # splitting training and test data
        # x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.3,random_state= 42)

        TfidfVect = TfidfVectorizer()
        TfidfVect.fit(x)

        path_ = modelPath + '/' + searchString
        # saving this tfidf model so that it can be utilized during prediction
        with open(path_ + '__tfidfVect.pickle', 'wb') as f:
            pickle.dump(TfidfVect, f)

        x_vector = TfidfVect.transform(x)
        # x_test_vector = TfidfVect.transform(x_test)

        # training data using SVM
        svm_model = naive_bayes.MultinomialNB()
        svm_model.fit(x_vector, y)
        # y_pred = model.predict(x_test_vector)
        # score1 = metrics.accuracy_score(y_test, y_pred)

        # saving SVM model for use while predicting
        with open(path_ + 'SVM_model.pickle', 'wb') as f:
            pickle.dump(svm_model, f)

        return "success"
