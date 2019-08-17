# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import lxml.html


from scrapy.exceptions import DropItem
from blogshopscrapy import settings
import logging


class BlogshopscrapyPipeline(object):

    def __init__(self, mongodb_server, mongodb_port, mongodb_collection, mongodb_db):
        self.mongodb_server = mongodb_server
        self.mongodb_port = mongodb_port
        self.mongodb_collection = mongodb_collection
        self.mongodb_db = mongodb_db
        self.parsedUrls = {}


    @classmethod
    def from_crawler(cls, crawler):
        # pull in info from settings.py to use in init method
        return cls(
            mongodb_server=crawler.settings.get('MONGODB_SERVER'),
            mongodb_port=crawler.settings.get('MONGODB_PORT'),
            mongodb_collection=crawler.settings.get('MONGODB_COLLECTION'),
            mongodb_db=crawler.settings.get('MONGODB_DB')
        )

    def open_spider(self, spider):
        # open db connection
        self.client = pymongo.MongoClient(self.mongodb_server, self.mongodb_port)
        self.db = self.client[self.mongodb_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # print("item::::::::::::::::::::::::", item)

        # Item types
        item_type_tags = {'dress': ['dress', 'one-piece'],
                          'skirts': ['skirt', 'bottoms'],
                          'shorts': ['shorts', 'bottoms'],
                          'tops': ['top'],
                          'pants': ['pants', 'bottoms'],
                          'romper': ['romper', 'one-piece'],
                          'one-piece': ['one-piece'],
                          'onepiece': ['one-piece'],
                          'blouse': ['top'],
                          'culottes': ['pants', 'bottoms'],
                          }

        valid = True
        for key in item:
            if key == 'itemName':
                tree = lxml.html.fromstring(
                    item[key]) # removes html tags from product name.Some have <br>, making it unable to use .text()
                item[key] = tree.text_content().strip()

            if key == 'itemPrice':
                if item[key] is None:
                    print("no promo price, set as 0 dollar")
                    item[key] = "SGD0"
                if 'SGD' in item[key]:
                    item[key] = item[key].replace('SGD', '').strip()

            if key == 'itemType':
                for cat_name in item_type_tags:
                    if cat_name in item['itemUrl']:
                        item[key] = item_type_tags[cat_name]
                        break
                    if cat_name in item['pageName']:
                        item[key] = item_type_tags[cat_name]
                        break
                    if item[key] == "":
                        item[key] = ['others']

            if key == 'itemImageUrl':
                if item[key] is None:
                    item[key] = ""

            if key == 'itemUrl':
                if item[key] is None:
                    item[key] = ""

                # --- REMOVE DUPLICATES ITEM_URLS --- TTR has the same urls with and without / under the /product page
                if item[key][:1] != '/':
                    item[key] = "/" + item[key]

                if item[key] not in self.parsedUrls:
                    self.parsedUrls[item[key]] = 1
                    # print("write!")
                else:
                    self.parsedUrls[item[key]] += 1
                    print("dupe found!!!!!" + item[key])
                    raise DropItem("Missing {0}!".format(item))
        if valid:
            # set itemUrl as primary key, update all other fields, increment crawlCount to track which are newly added
            self.db[self.mongodb_collection].update({'_id': item['itemUrl']},
                                                    {"$inc": {'crawlCount': 1}, "$set": dict(item)}, upsert=True)
            # self.db[self.mongodb_collection].insert(dict(item))
            logging.info("Added into MongoDB!")
        return item
