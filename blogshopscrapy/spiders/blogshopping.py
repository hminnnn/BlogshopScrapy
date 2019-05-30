# -*- coding: utf-8 -*-
import scrapy
import configparser
import lxml.html

from blogshopscrapy.items import BlogshopscrapyItem

# load config
config = configparser.ConfigParser()
config.read('...\\.\\..\\resources\\blogshop-properties.ini')
runOnePage = False

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

blogshop_names_dict = {'thetinselrack': 'TTR',
                       'shopsassydream': 'SSD'}


def writeToFile(blogshopitem, blogshopname, current_page_url, item_name, item_price, item_type, item_url, item_imageUrl):
    # print("writing")
    blogshopitem['baseUrl'] = config[blogshopname]['START_URL']
    blogshopitem['shopNameValue'] = blogshopname
    blogshopitem['pageName'] = current_page_url
    blogshopitem['itemName'] = item_name
    blogshopitem['itemPrice'] = item_price
    blogshopitem['itemType'] = item_type
    blogshopitem['itemUrl'] = item_url
    blogshopitem['itemImageUrl'] = item_imageUrl
    return blogshopitem


class BlogshoppingSpider(scrapy.Spider):
    name = 'blogshopping'
    allowed_domains = ['thetinselrack.com', 'shopsassydream.com']
    # start_urls = ['https://www.thetinselrack.com', 'https://www.shopsassydream.com']
    start_urls = ['https://www.shopsassydream.com']
    # start_urls = ['https://www.thetinselrack.com/category/apparel']

    def parse(self, response):
        # pass
        print("processing:" + response.url)

        global parsedUrls
        global runOnePage
        parsedUrls = {}
        if response.status == 200:

            # print out config file
            # f = open("...\\.\\..\\resources\\blogshop-properties.ini", "r")
            # contents = f.read()
            # print(contents)

            # parse which blogshop
            for name in blogshop_names_dict:
                if name in response.url:
                    blogshopname = blogshop_names_dict[name]
                    # print("currently running:", blogshopname)
                    break

            # get available categories to be parsed
            category_css = config[blogshopname]['CATEGORY']
            categories = response.css(category_css).extract()

            if runOnePage:  # only one page for testing
                yield scrapy.Request(
                    response.urljoin(response.url),
                    callback=self.parseCategory, meta={'blogshopname': blogshopname})
            else:
                categories = list(set(categories))  # store in map to remove duplicates
                # print(categories)
                for a in categories:
                    if a:
                        next_page = response.urljoin(a)
                        # print("heading to:", next_page)
                        yield scrapy.Request(response.urljoin(next_page), callback=self.parseCategory,
                                             meta={'blogshopname': blogshopname})

    # Parse details on each page for each category
    def parseCategory(self, response):

        current_page_url = response.url
        blogshopname = response.meta.get('blogshopname')

        # print("blogshopname:", blogshopname)
        # print("page url:", response.url)

        blogshopitem = BlogshopscrapyItem()

        product_rows = response.xpath(config[blogshopname]['PRODUCT_ROW'])

        for item in product_rows:
            print("item:", item)
            # --- PRODUCT NAME ---
            item_name = item.xpath(config[blogshopname]['ITEM_NAME']).extract_first()
            tree = lxml.html.fromstring(
                item_name)  # removes html tags from product name. Some names have <br>, making it unable to use .text()
            item_name = tree.text_content().strip()

            # --- PRODUCT PRICE ---
            item_price = item.xpath(config[blogshopname]['ITEM_PRICE']).extract_first()
            if item_price is None:  # Catch the promo price. Diff selector from normal price
                print("noneeeeeeeeee")
                item_price = item.xpath(config[blogshopname]['ITEM_PRICE_2']).extract_first()
            if item_price is None:
                item_price = "SGD0"

            # --- PRODUCT URL ---
            item_url = item.css(config[blogshopname]['ITEM_URL']).extract_first()
            if item_url is None:
                item_url = ""

            # --- PRODUCT TYPE ---
            item_type = ""
            for cat_name in item_type_tags:
                if cat_name in item_url:
                    item_type = item_type_tags[cat_name]
                    break
                if cat_name in current_page_url:
                    item_type = item_type_tags[cat_name]
                    break
            if item_type == "":
                item_type = ['others']

            # --- PRODUCT IMAGE ---
            item_imageUrl = item.css(config[blogshopname]['ITEM_IMAGEURL']).extract_first()
            if item_imageUrl is None:
                item_url = ""


            # print("item_name:", item_name)
            # print("item_price:", item_price)
            # print("item_url:", item_url)
            # print("item_type:", item_type)
            print("item_imageUrl:", item_imageUrl)

            # --- REMOVE DUPLICATES ITEM_URLS --- TTR has the same urls with and without / under the /product page
            if item_url[:1] != '/':
                item_url = "/" + item_url

            # --- CHECK FOR DUPES IN ALREADY PARSED URLS ---  will have dupes as all appear again at main apparels page
            if item_url not in parsedUrls:
                parsedUrls[item_url] = 1
                blogshopitem = writeToFile(blogshopitem, blogshopname, current_page_url, item_name, item_price, item_type, item_url, item_imageUrl)
                yield blogshopitem
            else:
                parsedUrls[item_url] += 1
                # print("dupe found!!!!!" + item_url)

        if not runOnePage:
            # Next page
            next_page = response.css(config[blogshopname]['NEXT_PAGE_SELECTOR']).extract_first()
            # print(next_page)
            if next_page:
                yield scrapy.Request(
                    response.urljoin(next_page),
                    callback=self.parseCategory, meta={'blogshopname': blogshopname})
