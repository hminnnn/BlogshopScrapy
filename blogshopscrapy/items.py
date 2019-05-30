# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BlogshopscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    baseUrl = scrapy.Field()
    shopNameValue = scrapy.Field()
    pageName = scrapy.Field()
    itemName = scrapy.Field()
    itemPrice = scrapy.Field()
    itemType = scrapy.Field()
    itemUrl = scrapy.Field()
    itemImageUrl = scrapy.Field()
    # pass
