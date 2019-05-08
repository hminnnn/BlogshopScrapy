# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

# from scrapy.exceptions import DropItem
from blogshopscrapy import settings
import logging


class BlogshopscrapyPipeline(object):

    def __init__(self, mongodb_server, mongodb_port, mongodb_collection, mongodb_db):
        self.mongodb_server = mongodb_server
        self.mongodb_port = mongodb_port
        self.mongodb_collection = mongodb_collection
        self.mongodb_db = mongodb_db


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
        valid = True
        for data in item:
            if not data:
                valid = False
                # raise DropItem("Missing {0}!".format(data))
        if valid:
            self.db[self.mongodb_collection].insert(dict(item))
            logging.info("Added into MongoDB!")
        return item
