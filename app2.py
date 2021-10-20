from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from urllib.parse import quote
import urllib
import logging
import pymongo
import numpy as np

app = Flask(__name__)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("my_project_web_scrapper.log")
formatter = logging.Formatter("%(asctime)s : %(lineno)d : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)



client = pymongo.MongoClient("mongodb+srv://yogesh_mongodb:" +quote("yogesh@12345") +"@webscrapsflipkart.1c9wo.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client["demo_scrapper_assignment"]  # connect to database




@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()   # we use this when we are deploying on server, as it helps to communicate to server in other region
def homePage():
    return render_template("index.html")


@app.route('/review', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():

    if request.method == 'POST':

        try:

            global searchString
            searchString = request.form['content'].replace(" ", "")
            searchString = searchString.lower()
            flipkart_url = "https://www.flipkart.com" + "/search?q=" + searchString + "&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"


            logger.info("Start of new program "+searchString)
            logger.info("")

            all_500_product_link = []
            page_num = 1


####################------------------------------------------------####################################################
            try:

                # user_name_atlas = "yogesh_mongodb"
                # pwd_for_atlas = "yogesh@12345"

                all_products_info = db[searchString].find({})  # searching the collection with the name same as the keyword

                if all_products_info.count() >= 500:  ###########make it 500
###################------
                    # if there is a collection with searched keyword and it has records in it
                    logger.info("records for " + searchString + " query are already there in db..")
                    # write that info is already available


                else:

                    all_products_info = []
                    while len(all_500_product_link) < 500 and page_num < 25:

                        try:

                            with uReq(flipkart_url + "&page=" + str(page_num)) as uClient:  # request webpage for the search query
                                flipkartPage = uClient.read()  # returns raw html for first page

                            fk_html = bs(flipkartPage, "html.parser")  # parsing webpage as html

                            if fk_html.find("div", {"class": "_3uTeW4"}):  # .text == "Sorry, no results found!" :
                                raise Exception()

                            #bigboxes = fk_html.findAll("div", {"class": "_1AtVbE col-12-12"})  # gives list of boxes
                            #bigboxes = bigboxes[2:-4]

                            # these are just the links for products in 1 page so, append them somewhere else as we want total
                            # of 500 products flipkart page has two types of list pages, so here 4 lines of code is to get
                            # all the products in the a single page
                            link_all_products_in_page = [i["href"] for i in fk_html.findAll("a", {"class": "_1fQZEK"},
                                                                                            href=True)]
                            # gives list of boxes for samsung type page
                            if len(link_all_products_in_page) == 0:
                                link_all_products_in_page = [i["href"] for i in fk_html.findAll("a", {"class": "_2rpwqI"})]  # gives list of boxes for xiomi type page

                            all_500_product_link.extend(link_all_products_in_page)  # add these product links to main list

                            #print(page_num)
                            page_num += 1  # focus page number to next page
                            # break

                            #if len(all_500_product_link) >= 500 or page_num > 25:     ##### len >= 500
                                #print("done")
                                #break
#############################-----------
                        except Exception as e:
                            logger.exception(fk_html.find("div", {"class": "_3uTeW4"}).text + "for" + flipkart_url + "&page=" + str(page_num))
                            break

                    number = 0

                    for product in all_500_product_link:

                        try:
                            with uReq("https://www.flipkart.com" + product) as uClient:  # request webpage for the search query
                                abc = uClient.read()  # returns raw html for first page
                        except Exception as e:
                            logger.exception(e)

                        fk_product_page = bs(abc, "html.parser")
                        searched_for = searchString

                        collection = db[searchString]  # creating a collection with the same name as search string. Tables and Collections are analogous.

                        ########################################
                        try:
                            product_name = fk_product_page.find("span", {"class": "B_NuCI"}).text
                        except:
                            logger.info("NO product_name for " + product)
                            product_name = ""
                        ##################################
                        try:
                            product_rating = float(fk_product_page.find("div", {"class": "gUuXy- _16VRIQ"}).span.div.text)
                        except:
                            logger.info("No product_rating for " + product)
                            product_rating = np.nan
                        #################################
                        try:
                            total_no_of_ratings = fk_product_page.find("span", {"class": "_2_R_DZ"}).span.span.text
                            total_no_of_ratings = float("".join(total_no_of_ratings.split(" ")[0].split(",")))
                        except:
                            logger.info("No total_no_of_ratings for " + product)
                            total_no_of_ratings = np.nan
                        #################################
                        try:
                            current_price = fk_product_page.find("div", {"class": "_30jeq3 _16Jk6d"}).text
                            current_price = float("".join(current_price.split(","))[1:])
                        except:
                            logger.info("No current price for " + product)
                            current_price = np.nan
                        ################################
                        try:
                            price_without_discount = fk_product_page.find("div", {"class": "_3I9_wc _2p6lqe"}).text

                            price_without_discount = float("".join(price_without_discount.split(","))[1:])
                        except Exception as e:
                            logger.info("No price_without_discount for " + product)
                            logger.exception(e)
                            price_without_discount = current_price
                        ################################
                        available_offers = []
                        try:
                            for i in fk_product_page.find_all("li", {"class": "_16eBzU col"}):
                                available_offers.append(i.text)
                        except:
                            pass
                        ##################################
                        try:
                            highlights = []
                            try:
                                for i in fk_product_page.find_all("div", {"class": "_2418kt"}):
                                    try:
                                        for j in i.find_all("li"):
                                            highlights.append(j.text)
                                    except:
                                        pass
                            except:
                                pass
                        except Exception as e:
                            logger.exception(e)
                        #####################################
                        try:
                            highlights_feature_2_title = ""
                            highlights_feature_2_title = fk_product_page.findAll("div", {"class": "_1AtVbE col-6-12"})[
                                1].div.div.text
                            highlights_feature_2 = []
                            try:
                                for i in fk_product_page.findAll("div", {"class": "_1AtVbE col-6-12"})[1].div:
                                    try:
                                        for j in i.findAll("li"):
                                            highlights_feature_2.append(j.text)
                                    except:
                                        pass
                            except:
                                pass

                        except Exception as e:
                            logger.exception(e)
                        ########################################
                        try:
                            seller = fk_product_page.find("div", {"class": "_1RLviY"}).text
                        except:
                            seller = ""
                        ##########################################
                        try:
                            description = fk_product_page.find("div", {"class": "_1mXcCf RmoJUa"}).p.text
                        except:
                            description = ""
                        ###########################################
                        specifications = {}
                        try:
                            for i in fk_product_page.find("div", {"class": "_1UhVsV"}).findAll("div", {"class": "_3k-BhJ"}):
                                try:
                                    spec_title = i.find("div", {"class": "flxcaE"}).text
                                    if spec_title == "Important Note:":
                                        continue

                                    spec_name_dict = {}
                                    try:
                                        for j in i.find("table", {"class": "_14cfVK"}).findAll("tr"):
                                            spec_name = j.td.text
                                            spec = j.ul.text
                                            spec_name_dict[spec_name] = spec
                                            specifications[spec_title] = spec_name_dict
                                    except Exception as e:
                                        logger.exception(e)
                                        del spec_title
                                        del spec_name
                                        logger.info(spec_title + " and " + spec_name + " have been deleted for some error")
                                except Exception as e:
                                    logger.exception(e)
                        except Exception as e:
                            logger.exception(e)
                        #############################################################
                        commentboxes = fk_product_page.find_all('div', {'class': "_16PBlm"})
                        random_cust_comments = []

                        for commentbox in commentboxes[:-1]:

                            try:
                                # name.encode(encoding='utf-8')
                                cust_name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                            except:
                                cust_name = 'No Name'

                            try:
                                # rating.encode(encoding='utf-8')
                                cust_given_ratings = commentbox.div.div.div.div.text
                            except:
                                cust_given_ratings = 'No Rating'

                            try:
                                # commentHead.encode(encoding='utf-8')
                                comment_head = commentbox.div.div.div.p.text
                            except:
                                comment_head = 'No Comment Heading'

                            try:
                                comtag = commentbox.div.div.find_all('div', {'class': ''})
                                # custComment.encode(encoding='utf-8')
                                comment = comtag[0].div.text
                            except Exception as e:
                                comment = "No comment"
                                logger.info("Exception while creating dictionary: ", e)

                            new_comment = {"cust_name": cust_name,
                                           "cust_given_ratings": cust_given_ratings,
                                           "Comment_head": comment_head,
                                           "comment": comment
                                           }
                            random_cust_comments.append(new_comment)
                        ###################################################
                        # what to extract
                        # dictionary to enter
                        new_product_info = {
                            "searched_for": searched_for,
                            "product_name": product_name,
                            "product_rating": product_rating,
                            "total_no_of_ratings": total_no_of_ratings,
                            "current_price": current_price,
                            "price_without_discount": price_without_discount,
                            "available_offers": available_offers,
                            "highlights": highlights,
                            highlights_feature_2_title: highlights_feature_2,
                            "seller": seller,
                            "description": description,
                            "specifications": specifications,
                            "random_cust_comments": random_cust_comments
                        }
                        try:
                            x = collection.insert_one(new_product_info)
                            # inserting to the atlas one at a time
                        except Exception as e:
                            logger.exception(e)
                            #print(new_product_info)

                        all_products_info.append(new_product_info)
                        number += 1
                        # print(number)
                        if number >= 510:   # delete it later, as it is not required..
                            break

                return render_template('results.html', all_products_info=all_products_info, searchString=searchString)

            except Exception as e:
                logger.exception(e)


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
