# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class MovieItem(Item):
	source = Field()
	title = Field()
	desc = Field()
	resource = Field()
	
	file_urls = Field()
	files = Field()
