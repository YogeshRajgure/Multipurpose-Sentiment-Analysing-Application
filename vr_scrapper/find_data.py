from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def find_data_on_fk(searchString, n_comments, multiproducts, multiproducts_counter, logger, db):

    """

    :param searchString:
    :param n_comments:
    :param multiproducts:
    :param multiproducts_counter:
    :param logger:
    :param db:
    :return: nothing

    This function is responsible for:
    -searching the topic on the flipkart
    -storing all the comments to the mongodb atlas
    -making all logs about it

    """

    flipkart_url = "https://www.flipkart.com" + "/search?q=" + searchString + "&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"

    logger.info("Start of new program " + searchString)
    logger.info("")

    collection = db[searchString]

    # webdriver handler
    wd = webdriver.Chrome(executable_path='./chromedriver.exe')
    wd.get(flipkart_url)  # get the website
    wd.maximize_window()

    links_to_all = wd.find_elements_by_class_name("_2rpwqI")  # _2r_T1I         # links_to_all the products on the page
    if len(links_to_all) == 0:
        links_to_all = wd.find_elements_by_class_name("_1fQZEK")
    if len(links_to_all) == 0:
        links_to_all = wd.find_elements_by_class_name("_2r_T1I")

    product_link_count = 0
    a = links_to_all[product_link_count].click()

    counter = 0
    all_comments = list()
    comment_interfering_flag = 0

    while counter <= n_comments:

        # we switch to new handle for new tab
        new_tab_handler = wd.window_handles[-1]
        wd.switch_to.window(new_tab_handler)

        # here we click on more comments
        try:
            if len(wd.find_elements_by_xpath('//div[@class="col JOpGWq"]/a')) != 0:
                wd.find_element_by_xpath('//div[@class="col JOpGWq"]/a').click()
            else:
                wd.find_element_by_xpath('//div[@class="col JOpGWq _33R3aa"]/a').click()

        except Exception as e:
            # go to the next product using saved link of all products
            product_link_count += 1
            if product_link_count > 20:
                print("not enough comments")
            # set acting handler to first tab which contains all the products
            new_tab_handler = wd.window_handles[0]
            wd.switch_to.window(new_tab_handler)

            links_to_all[product_link_count].click()
            logger.exception(e)

            continue

        # below code makes sure that webpage is loaded
        delay = 3  # seconds
        try:
            myElem = WebDriverWait(wd, delay).until(EC.presence_of_element_located((By.CLASS_NAME, '_1LKTO3')))
            logger.info("Comments page is ready")
            print("comments Page is ready!")
        except TimeoutException as e:
            logger.exception(e)

        # occurance of 'previous page' button is not possible at this stage as it is first page and only has 'next' button
        prev = 0

        while True:

            full_cmt_data = wd.find_elements_by_css_selector('._27M-vq')
            # has 10 comments data

            # this loop checks for every comment in that page
            for new_cmt in full_cmt_data:

                comment_text = new_cmt.text  # get all the text present in comment box
                comment_text = comment_text.split("\n")

                comment_rating = comment_text[0]  # comment ratings
                comment_text = ' '.join(comment_text[1:-4])  # comment text

                if len(comment_text) < 1:
                    # comment_rating = ' '.join(comment_rating)
                    comment_text = comment_rating[1:]
                    comment_rating = comment_rating[0]  # [0]

                if len(comment_rating) > 1:
                    comment_text = comment_rating[1:] + ' ' + comment_text
                    comment_rating = comment_rating[0]

                new_comment = {
                    "ratings": comment_rating,
                    "comment": comment_text
                }
                all_comments.append(new_comment)  # append to the list
                counter += 1

            logger.info("Done with taking all comments from 1 page of comment")
            print("done")

            # upload to database
            try:
                x = collection.insert_many(all_comments)
                #print(all_comments)
            except Exception as e:
                logger.exception(e)
            # clear cotent from all_comments
            all_comments = []
            logger.info("all comments from 1 page uploaded to database.")
            # this line will click on next from 2nd page of comments as it has prev and next button with same class name
            links = wd.find_elements_by_xpath('//a[@class="_1LKTO3"]')
            if (prev == 1 and len(links) == 1) or len(links) == 0:
                break

            wd.get(links[-1].get_attribute('href'))
            prev = 1
            print('executed')

            if multiproducts and counter > multiproducts_counter:

                product_link_count += 1
                # switch back to first fk page
                new_tab_handler = wd.window_handles[0]
                wd.switch_to.window(new_tab_handler)
                # click in the next product
                links_to_all[product_link_count].click()

                multiproducts_counter = (n_comments // 4) * multiproducts
                multiproducts += 1

            if counter > n_comments:
                break

    print("all done")
