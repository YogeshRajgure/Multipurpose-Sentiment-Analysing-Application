from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import logging
import pymongo
from urllib.parse import quote
import ssl

# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import TimeoutException


from vr_scrapper.find_data import find_data_on_fk
from vr_scrapper.abc import find_data_on_fk_dummy

app = Flask(__name__)

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



@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()   # we use this when we are deploying on server, as it helps to communicate to server in other region
def homePage():
    return render_template("index.html")#"train_model.html")#


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

            #find_data_on_fk_dummy(searchString, n_comments, multiproducts, multiproducts_counter, logger, db)
            find_data_on_fk(searchString, n_comments, multiproducts, multiproducts_counter, logger, db)

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
        return render_template('index.html')




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
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)
