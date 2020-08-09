# blogshopscrapy
trying out scrapy 
- parses 2 sites and stores data in mongodb 


#### To run manually
> /Blogshopscrapy > scrapy crawl blogshopping


#### To scrap only one page to check response (to identify classnames and tags)
- scrapy shell  
- fetch(url)  
- view(response)  
- print(response.text)

#### Files

spiders/blogshopping.py - spider

items.py - database fields

pipelines.py - process items to write to db

resources/blogshop-properties.ini - blogshop tags 

#### Sites parsed

start_urls = ['https://www.thetinselrack.com', 'https://www.shopsassydream.com']