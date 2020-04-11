# -*- coding: utf-8 -*-
import scrapy
import configparser
from scrapy.crawler import CrawlerProcess


from blogshopscrapy.items import BlogshopscrapyItem

# load config
config = configparser.ConfigParser()
config.read('...\\.\\..\\resources\\blogshop-properties.ini')
runOnePage = False
maxPagesPerSection = 50

blogshop_names_dict = {'thetinselrack': 'TTR',
                       'shopsassydream': 'SSD'}


def writeToFile(blogshopitem, blogshopname, current_page_url, item_name, item_price, item_type, item_url,
                item_imageUrl, item_page_no):
    print("writing")
    blogshopitem['baseUrl'] = config[blogshopname]['START_URL']
    blogshopitem['shopNameValue'] = blogshopname
    blogshopitem['pageName'] = current_page_url
    blogshopitem['itemName'] = item_name
    blogshopitem['itemPrice'] = item_price
    blogshopitem['itemType'] = item_type
    blogshopitem['itemUrl'] = item_url
    blogshopitem['itemImageUrl'] = item_imageUrl
    blogshopitem['dateCrawled'] = ""
    blogshopitem['crawlCount']= item_page_no
    return blogshopitem


class BlogshoppingSpider(scrapy.Spider):
    name = 'blogshopping'
    allowed_domains = ['thetinselrack.com', 'shopsassydream.com']
    start_urls = ['https://www.thetinselrack.com', 'https://www.shopsassydream.com']
    # start_urls = ['https://www.thetinselrack.com']
    if runOnePage:
        start_urls = ['https://www.thetinselrack.com/category/apparel']

    def parse(self, response):

        global runOnePage
        if response.status == 200:

            # print out config file
            # f = open("...\\.\\..\\resources\\blogshop-properties.ini", "r")
            # contents = f.read()
            # print(contents)

            # identify which blogshop is the current response from
            for name in blogshop_names_dict:
                if name in response.url:
                    blogshopname = blogshop_names_dict[name]
                    break

            # get available categories to be parsed
            category_css = config[blogshopname]['CATEGORY']
            categories = response.css(category_css).extract()

            if runOnePage:  # only one page for testing
                yield scrapy.Request(
                    response.urljoin(response.url),
                    callback=self.parseCategory, meta={'blogshopname': blogshopname, 'count': 0})
            else:
                categories = list(set(categories))  # store in map to remove duplicates
                print(categories)
                for a in categories:  # loop through all pages in
                    if a:
                        next_page = response.urljoin(a)
                        yield scrapy.Request(response.urljoin(next_page), callback=self.parseCategory,
                                             meta={'blogshopname': blogshopname, 'count': 0})

    # ------- Parse details on each page for each category -------
    def parseCategory(self, response):
        global maxPagesPerSection
        if response.meta.get('count') > maxPagesPerSection:
            print("ok no. of pages is now: ", response.meta.get('count'))
            return None

        print("current page: ", response.meta.get('count'))

        current_page_url = response.url
        blogshopname = response.meta.get('blogshopname')

        blogshopitem = BlogshopscrapyItem()

        product_rows = response.xpath(config[blogshopname]['PRODUCT_ROW'])

        for item in product_rows:
            # --- PAGE NUMBER FOR RANKING ---
            item_page_no = response.meta.get('count')

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
            blogshopitem = writeToFile(blogshopitem, blogshopname, current_page_url, item_name, item_price, item_type,
                                       item_url, item_imageUrl, item_page_no)
            yield blogshopitem

        if not runOnePage:
            # Next page
            next_page = response.css(config[blogshopname]['NEXT_PAGE_SELECTOR']).extract_first()
            if next_page:
                yield scrapy.Request(
                    response.urljoin(next_page),
                    callback=self.parseCategory,
                    meta={'blogshopname': blogshopname, 'count': response.meta.get('count') + 1})

# To run from here instead of the command 'scrapy crawl blogshopping' -- Doesnt work probably due to virtual env.
# process = CrawlerProcess()
# process.crawl(BlogshoppingSpider)
# process.start()
