# -*- coding: utf-8 -*-
import scrapy
import configparser
import lxml.html

from blogshopscrapy.items import BlogshopscrapyItem

# load config
config = configparser.ConfigParser()
config.read('...\\.\\..\\resources\\blogshop-properties.ini')
runOnePage = False

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
    start_urls = ['https://www.thetinselrack.com', 'https://www.shopsassydream.com']
    # start_urls = ['https://www.thetinselrack.com']
    if runOnePage:
        start_urls = ['https://www.thetinselrack.com/category/apparel']

    def parse(self, response):
        # pass
        # print("processing:" + response.url)

        global runOnePage
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

        blogshopitem = BlogshopscrapyItem()

        product_rows = response.xpath(config[blogshopname]['PRODUCT_ROW'])

        for item in product_rows:

            # --- PRODUCT NAME ---
            item_name = item.xpath(config[blogshopname]['ITEM_NAME']).extract_first()

            # --- PRODUCT PRICE ---
            item_price = item.xpath(config[blogshopname]['ITEM_PRICE']).extract_first()
            if item_price is None:  # Catch the promo price. Diff selector from normal price
                print("no normal price, taking promo price")
                item_price = item.xpath(config[blogshopname]['ITEM_PRICE_2']).extract_first()

            # --- PRODUCT URL ---
            item_url = item.css(config[blogshopname]['ITEM_URL']).extract_first()

            # --- PRODUCT TYPE ---
            item_type = ""

            # --- PRODUCT IMAGE ---
            item_imageUrl = item.css(config[blogshopname]['ITEM_IMAGEURL']).extract_first()

            # Process at pipelines
            blogshopitem = writeToFile(blogshopitem, blogshopname, current_page_url, item_name, item_price, item_type, item_url, item_imageUrl)
            yield blogshopitem

        if not runOnePage:
            # Next page
            next_page = response.css(config[blogshopname]['NEXT_PAGE_SELECTOR']).extract_first()
            # print(next_page)
            if next_page:
                yield scrapy.Request(
                    response.urljoin(next_page),
                    callback=self.parseCategory, meta={'blogshopname': blogshopname})
