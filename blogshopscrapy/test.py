import configparser
from datetime import date

from blogshopscrapy import settings

from lxml import html
import requests


class test():

    # config = configparser.ConfigParser()
    # config.read('..\\..\\resources\\blogshop-properties.ini')
    # print("hiiii")
    #
    # temp = 'TTR'
    #
    # f=open("..\\..\\resources\\blogshop-properties.ini","r")
    # contents = f.read()
    # print(contents)
    # print(config.sections())
    # print(config[temp]['CATEGORY_CSS'])

    # print(settings['MONGODB_SERVER'])

    # page = requests.get('https://www.sgpbusiness.com/company/Jay-Chia-Consulting')
    # tree = html.fromstring(page.content)
    # print(tree)


    today = date.today()
    print(today)