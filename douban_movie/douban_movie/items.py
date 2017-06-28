# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanMovieItem(scrapy.Item):
    # define the fields for your item here like:
    Tag = scrapy.Field()
    Movie_Name = scrapy.Field()
    Url = scrapy.Field()
    Rating_nums = scrapy.Field()
    Comment_nums = scrapy.Field()