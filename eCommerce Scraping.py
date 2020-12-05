from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from config import *
from datetime import datetime
from time import sleep
import sqlite3
from sqlite3 import Error
import os

try:
    current_path = os.path.dirname( os.path.abspath(__file__ ) )

except:
    current_path = ''
    

create_table_sql = """ CREATE TABLE IF NOT EXIStS products_info
    (product_title TEXT, product_url TEXT NOT NULL, img_url TEXT, product_price INTERGER NO NULL, 
    product_description TEXT, product_review TEXT, product_stars TEXT, inserted_at TEXT)
            """

conn = sqlite3.connect(f"{current_path}/sql.db")
cr = conn.cursor()
cr.execute(create_table_sql)

def init_driver(load_image = True , user_agent = '', is_headless = is_headless):
    firefox_profile = webdriver.FirefoxProfile()

    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', False) #Displayed flashPlayer
    firefox_profile.set_preference("media.volume_scale", "0.0") #No volume
    firefox_profile.set_preference("dom.webnotifications.enabled", False) #No notifications

    if load_image == False:
        firefox_profile.set_preference('permissions.default.image', 2) # Load image 2 = Not load Image
    
    if user_agent != '':
        firefox_profile.set_preference("general.useragent.override", user_agent) #user agent

    options = Options()

    options.headless = is_headless

    driver = webdriver.Firefox(firefox_profile = firefox_profile , options = options,)
    
    return driver

def get_url(driver , base_site_url):
    driver.get(base_site_url)

    sleep(2)
    if len(driver.find_elements_by_css_selector("#cookieBanner #closeCookieBanner")) > 0:
        close_cookie_banner = driver.find_elements_by_css_selector("#cookieBanner #closeCookieBanner")[0]

        close_cookie_banner.click()


def get_products(driver, products):
    products_info = []

    for product in products:

        img_url = ''
        if len(product.find_elements_by_css_selector("div.thumbnail .img-responsive")) > 0:

            img = product.find_elements_by_css_selector("div.thumbnail .img-responsive")[0]

            img_url = img.get_attribute('src')

        product_title = ''
        product_url = ''

        if len(product.find_elements_by_css_selector('.caption a.title')) > 0:

            product_title = product.find_elements_by_css_selector('.caption a.title')[0].text

            product_url = str(product.find_elements_by_css_selector('.caption a.title')[0].get_attribute('onclick'))

            print(product_url)
            product_url = product_url[21:]

            product_url = product_url[:-45]

        product_price = ''
        if len(product.find_elements_by_css_selector('.pull-right.price')) > 0:

            product_price = product.find_elements_by_css_selector('.pull-right.price')[0].text

        
        product_description = ''
        if len(product.find_elements_by_css_selector('.description')) > 0:

            product_description = product.find_elements_by_css_selector('.description')[0].text

        product_review = 0
        if len(product.find_elements_by_css_selector('.ratings .pull-right')) > 0:

            product_review = product.find_elements_by_css_selector('.ratings .pull-right')[0].text

        product_stars = 0
        if len(product.find_elements_by_css_selector('.ratings p[data-rating]')) > 0:

            product_stars = product.find_elements_by_css_selector('.ratings p[data-rating]')[0].get_attribute('data-rating')

        product_info = [product_title, product_url, img_url, product_price, product_description, product_review, product_stars, datetime.now()]


        cr.execute(f"SELECT * FROM products_info WHERE product_title=?",(product_info[0],))
        row = cr.fetchall()

        if len(row) > 0:
            cr.execute(f"SELECT * FROM products_info WHERE product_price=?",(product_info[3],))
            prod = cr.fetchall()
            if len(prod) == 0:
                cr.execute("UPDATE products_info SET product_price=? WHERE product_title=?", (product_info[3],product_info[0],))
                conn.commit()
        else:
            cr.execute("INSERT INTO products_info(product_title, product_url, img_url, product_price, product_description, product_review, product_stars, inserted_at) VALUES(?,?,?,?,?,?,?,?)", (product_info[0],product_info[1],product_info[2],product_info[3],product_info[4],product_info[5],product_info[6],product_info[7]))
            conn.commit()


        products_info.append(product_info)

    return products_info




driver = init_driver()

get_url(driver, base_site_url)

categories = [ 'computers/laptops', 'computers/tablets', 'phones/touch' ]


for category in categories:
    get_url(driver, f"{base_site_url}/{category}")

    sleep(3)

    products = driver.find_elements_by_css_selector("div.col-sm-4.col-lg-4.col-md-4")

    a = get_products(driver, products)

    sleep(load_timt_page)
