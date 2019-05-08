import configparser

from blogshopscrapy import settings


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

    print(settings['MONGODB_SERVER'])