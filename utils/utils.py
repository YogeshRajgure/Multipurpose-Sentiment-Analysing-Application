import os
import json
import re
import shutil
import string
import en_core_web_sm
import pandas as pd

def return_path_for_models(userId, projectId):
    base_path = os.path.join("training_data", userId, projectId)
    # here, we do not need to change the directory as we already changed it in checkForDirectory_and_models() function
    print(os.getcwd())
    os.chdir(base_path)

    for dir_name in os.listdir():
        if "model" in dir_name:
            svm_model = os.path.join(base_path, dir_name)
        if "tfidf" in dir_name:
            tfidf_vect = os.path.join(base_path, dir_name)

    for i in range(3): os.chdir("..")
    return svm_model, tfidf_vect

def checkForDirectory_and_models(userId, projectId ):
    path = os.path.join("training_data", userId, projectId)
    print("made path")
    if os.path.isdir(path):
        os.chdir(path)
        print("changed dir")
        if len(os.listdir()) >= 2 :
            print("greater than 2")
            check = 1
            for dir_name in os.listdir():
                if ("model" in dir_name):
                    break
            else:
                print("model is not found in location")
                for i in range(3):os.chdir("..")
                return False

            for dir_name in os.listdir():
                if ("tfidf" in dir_name):
                    break
            else:
                print("tfidf is not found in location")
                for i in range(3): os.chdir("..")
                return False
            for i in range(3): os.chdir("..")
            return True
        else:
            for i in range(3): os.chdir("..")
            return False

    else:
        return False

def createDirectoryForUser(userId, projectId):  # always creates directory under training data directory
    path = os.path.join("training_data", userId)  # .replace("\\","/")
    try:
        os.makedirs(path, exist_ok=True)
    except:
        if not os.path.isdir(path):
            os.mkdir(path)

    path = os.path.join("training_data", userId, projectId)  # .replace("\\","/")
    try:
        os.makedirs(path)
    except:
        if not os.path.isdir(path):
            os.mkdir(path)

    return path


def download_data_from_db(collection, path, searchString):
    data = [i for i in collection.find({}, {'_id': 0,
                                            'ratings': 1,
                                            'comment': 1
                                            }
                                       ).sort([('ratings', -1)])]
    all_data = {'data': data,
                'projectId': 'fk_data',
                'userId': 'frames'
                }
    path_ = os.path.join(path, searchString + "_train.json")

    with open(path_, "w") as f:
        f.write(json.dumps(all_data, indent=4, sort_keys=True))

    data_file_name = searchString + "_train.json"
    return data_file_name


def data_from_StopWords_File(filePath):
    print(filePath)
    stopWordsList = list()
    try:
        with open(filePath, 'r') as f:
            lines = f.read().splitlines()
    except:
        filePath.replace("\\","/")
        with open(filePath, 'r') as f:
            lines = f.read().splitlines()

    for line in lines:
        stopWordsList.append(line)

    return stopWordsList



def data_preprocessing_train(list_of_data_dict, stopWords_file_path):
    stopWords = data_from_StopWords_File(stopWords_file_path)
    nlp = en_core_web_sm.load()
    pattern = "@\S+|https?:\S+|http?:\S|[^A-Za-z0-9]+"

    # df = pd.DataFrame(columns=['target', 'text'])

    # our data is save as list of dictonaries
    for data in list_of_data_dict:
        line = data['comment']
        doc = nlp(line)
        clean_text = []

        for token in doc:
            clean = re.sub(pattern, '', str(token.lemma_).lower())
            if clean not in string.punctuation:
                if clean not in stopWords:
                    clean_text.append(clean)
        data['comment'] = " ".join(clean_text)  # converting preprocesed data from list to string to use in tfIdf

    df = pd.DataFrame(list_of_data_dict)
    df.columns = ['text', 'target']

    return df



def data_preprocessing_predict(text_list, stopWords_file_path):
    stopWords = data_from_StopWords_File(stopWords_file_path)
    nlp = en_core_web_sm.load()  # preprocessing library spacy
    pattern = "@\S+|https?:\S+|http?:\S|[^A-Za-z0-9]+"
    clean_text = []
    print("text_list : ",text_list)
    for data in text_list:
        print(data)
        clean_data = []
        doc = nlp(data)

        for token in doc:
            clean_token = re.sub(pattern, '', str(token.lemma_).lower())
            if clean_token not in string.punctuation:
                if clean_token not in stopWords:
                    clean_data.append(clean_token)
        clean_text.append(clean_data)
    print("clean_text : ", clean_text)

    return clean_text



def extractDataFromTrainingIntoDictionary(train_data):
    dict_train_data = {}
    # lNameList = []
    for dict in train_data:
        key_value = dict['lName']
        value = dict['lData']
        # lNameList.append(dict['lName'])
        if key_value not in dict_train_data.keys():
            dict_train_data[key_value] = list([value])
        else:
            (dict_train_data[key_value]).append(value)

    return dict_train_data



def deleteExistingTrainingFolder(path):
    try:
        # if os.path.isdir("ids/" + userName):
        if os.path.isdir(path):
            shutil.rmtree(path)
            return path + ".....deleted successfully.\n"
        else:
            print('File does not exists. ')
    except OSError as s:
        print(s)


# main function
def preprocess_training_data(json_file_path, stopWords_file_path):
    with open(json_file_path,'r') as f:
        all_data = json.load(f)
    # data cleaning
    clean_df = data_preprocessing_train(all_data['data'], stopWords_file_path)

    return clean_df















