from flask import Flask, render_template, request, Response, jsonify
from flask_cors import CORS, cross_origin
import logging
import pymongo
import ssl
import os

from vr_scrapper.find_data import find_data_on_fk
from utils import utils
from trainApp.trainApp import TrainApi
from predictApp.predictApp import PredictApi


# settings for log file
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("my_project_web_scrapper.log")
formatter = logging.Formatter("%(asctime)s : %(lineno)d : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)



# connect to database
url = "mongodb+srv://yogesh_mongodb:6OewcilbHWVDBkLu@data1.9xfe6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = pymongo.MongoClient(url, ssl_cert_reqs=ssl.CERT_NONE)
db = client["Scrapper_n_Sentiment"]


app = Flask(__name__)


class ClientApi:

    def __init__(self):
        stopWords_filePath = 'data\\stopwords.txt'
        self.trainObj = TrainApi(stopWords_filePath)
        self.predictObj = PredictApi(stopWords_filePath)



@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()   # we use this when we are deploying on server, as it helps to communicate to server in other region
def homePage():
    return render_template("start.html")#"make_new_model.html")# "index.html")#


@app.route('/fetch_n_store', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def page11_fetch_n_store():
    return render_template("fetch_n_store.html")

@app.route('/make_new_model', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def page12_make_new_model():
    return render_template("make_new_model.html")


@app.route('/test_model', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def page13_test_model():
    #return render_template("test_model.html")
    return render_template("predict_on_model.html")


@app.route('/review', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():

    if request.method == 'POST':

        try:
            global searchString
            global multiproducts
            global n_comments
            global User_Id
            global Project_Id
            global fetchNstore
            global makeNewModel

            searchString = request.form['content'].replace(" ", "")
            searchString = searchString.lower()
            n_comments = int(request.form['num'])
            User_Id = request.form['UserId_r']
            Project_Id = request.form['ProjectId_r']

            try:
                multiproducts = request.form['multi_products']
                multiproducts = int(1)
                multiproducts_counter = n_comments / 4
            except:
                multiproducts = 0
                multiproducts_counter = 0

            if "fetch_n_store" in str(request.__dict__['environ']['HTTP_REFERER']):
                fetchNstore  = 1
                makeNewModel = 0
            elif "make_new_model" in str(request.__dict__['environ']['HTTP_REFERER']):
                print("making new model")
                fetchNstore  = 0
                makeNewModel = 1

            # if search string is already available in mongodb
            if searchString in db.list_collection_names():
                # and if n_docs is sufficient
                logger.info("collection is already present")
                if db[searchString].count_documents(filter={}) >= n_comments:
                    # do not scrap the web, just use saved data from mongodb
                    logger.info("The data is already present on mongodb for requested query and is sufficient")
                    print("data is already present.")
                    # but
                    if makeNewModel == 1:
                        try:
                            path = utils.createDirectoryForUser(User_Id, Project_Id)
                            data_file_name = utils.download_data_from_db(db[searchString], path, searchString)
                            # probably try that, after this download, you can go to new page showing that your model is being trained.
                            json_file_path = path + '/' + data_file_name
                            model_score = new_client.trainObj.training_model(json_file_path, path, searchString)
                        except Exception as e:
                            logger.log(e)
                # and n_docs is not sufficient
                else:
                    logger.info("But not enough data as it is required")
                    # delete that collection and make new collection for same string
                    db[searchString].drop()
                    logger.info(f"collection {searchString} deleted as it had insufficient data.")
                    find_data_on_fk(searchString, n_comments, multiproducts, multiproducts_counter, logger, db)

            # if search string is not already available in mongodb
            else:
                #find_data_on_fk_dummy(searchString, n_comments, multiproducts, multiproducts_counter, logger, db)
                find_data_on_fk(searchString, n_comments, multiproducts, multiproducts_counter, logger, db)

            # this means that we not only have to store data on mongodb, but also gather it and pass it for model
            if makeNewModel == 1:
                # now, we have to make a directory and store the collected data at that location
                try:
                    path = utils.createDirectoryForUser(User_Id, Project_Id)
                    data_file_name = utils.download_data_from_db(db[searchString], path, searchString)
                    # probably try that, after this download, you can go to new page showing that your model is being trained.
                    json_file_path = path + '/' + data_file_name
                    model_score = new_client.trainObj.training_model(json_file_path, path, searchString)
                except Exception as e:
                    logger.log(e)
                pass

            return render_template('results.html', searchString=searchString)

        except Exception as e:
            logger.exception(e)
            return 'something went wrong'

        finally:
            logger.info(" ")
            logger.info("End Of Program")
            logger.info(" ")
            logger.info(" ")
            logger.info(" ")

    else:
        return render_template('start.html')



@app.route('/predict', methods=['POST'])
@cross_origin()
def predict_on_model():
    try:
        User_Id = request.form['UserId']
        Project_Id = request.form['ProjectId']
        text = request.form['predict_text']
        #text_ = list()
        #text_.append(text)
        print("h")
        if utils.checkForDirectory_and_models(User_Id, Project_Id):
            print("hi")
            svm_model, tfidf_vect = utils.return_path_for_models(User_Id, Project_Id)
            print("hii")
            result = new_client.predictObj.execute_processing(text, svm_model, tfidf_vect)
            pass
        else:
            logger.info("models not present")

    except Exception as e:
        logger.log(e)
        return Response((str(e)))
    return Response(result)






@app.route('/visualization', methods=['POST', 'GET'])
@cross_origin()
def graph():

    documentsWithTop50NoOfRatings = [i for i in db[searchString].find({}, {'product_name': 1,
                                                                      '_id': 0,
                                                                      'price_without_discount': 1,
                                                                      'current_price': 1,
                                                                      'product_rating': 1,
                                                                      'total_no_of_ratings': 1
                                                                     }
                                                                 ).sort([("total_no_of_ratings", -1),
                                                                        ("current_price", 1)
                                                                        ]
                                                                 ).limit(50)
                                    ]  # now, data contains iterable object for all the project names

    names_of_products = []  # [i['product_name'] for i in data]
    real_price_values = []  # [i['price_without_discount'] for i in data]
    current_price_values = []  # [i['current_price'] for i in data]
    ratings = []  # [i['product_rating'] for i in data]
    total_ratings = []
    for i in documentsWithTop50NoOfRatings:
        names_of_products.append(i['product_name'].split(')')[0]+')')
        real_price_values.append(i['price_without_discount'])
        current_price_values.append(i['current_price'])
        ratings.append(i['product_rating'])
        total_ratings.append(i['total_no_of_ratings'])

    return render_template("chart.html", total_ratings=total_ratings, searchString=searchString, names_of_products=names_of_products, real_price_values=real_price_values, current_price_values=current_price_values, ratings=ratings)





if __name__ == "__main__":

    new_client = ClientApi()
    # host = '0.0.0.0'
    # port = 5001
    # httpd = simple_server.make_server(host, port, app)
    # print("Serving on %s %d" % (host, port))
    # httpd.serve_forever()
    app.run(debug=True)
