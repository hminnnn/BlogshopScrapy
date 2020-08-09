import schedule
import time
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
# from spiders import blogshopping
from spiders.blogshopping import BlogshoppingSpider

# To run from here instead of the command 'scrapy crawl blogshopping'
# runner = CrawlerRunner()
# deferred = runner.crawl(BlogshoppingSpider)  # crawl() returns a deferred that is fired when the crawling is finished
# deferred.addBoth(lambda _: reactor.stop())

# print("running job again")
# runner = CrawlerRunner()
# print(runner)
# deferred = runner.crawl(BlogshoppingSpider)  # crawl() returns a deferred that is fired when the crawling is finished
# deferred.addBoth(lambda _: reactor.stop())
# reactor.run();

def job():
    print("running job again")
    runner = CrawlerRunner()
    deferred = runner.crawl(BlogshoppingSpider)  # crawl() returns a deferred that is fired when the crawling is finished
    print(deferred)
    deferred.addBoth(lambda _: reactor.stop())
    reactor.run();


schedule.every().day().at("20:00").do(job)
print("scheduling")
# schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    print("goingtosleep")
    time.sleep(3600)
