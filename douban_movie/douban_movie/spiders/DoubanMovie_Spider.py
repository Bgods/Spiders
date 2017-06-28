#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Bgods
# @Date:   2017-06-19 23:28:48
# @Last Modified by:   Bgods
# @Last Modified time: 2017-06-22 19:10:12

from scrapy.spiders import Spider
from douban_movie.items import DoubanMovieItem
from douban_movie.pipelines import DoubanMoviePipeline
from scrapy.http import Request
import re
import urllib.request

class DoubanMovieSpider(Spider):
    name = 'DoubanMovie'
    allowed_domains = ['movie.douban.com']
    tag = [u'爱情',u'科幻',u'青春',u'搞笑',u'战争',u'传记',u'家庭',u'浪漫',u'烂片',u'喜剧',u'动作',u'犯罪',u'纪录片',u'黑色幽默',u'情色',u'音乐',u'女性',u'史诗',u'剧情',u'经典',u'惊悚',u'励志',u'短片',u'感人',u'动画短片',u'黑帮',u'童话',u'动画',u'悬疑',u'文艺',u'恐怖',u'魔幻',u'暴力',u'童年',u'同志',u'西部']
    
    start_urls = ["https://movie.douban.com/tag/%s" % t for t in tag]
    headers = {
        "Host": "movie.douban.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }

    def make_requests_from_url(self, url):
        return Request(url, dont_filter=True, headers=self.headers)

    def parse(self, response):
        current_url = urllib.request.unquote(response.url)

        tag = re.sub(r"\?(.*)","",current_url)
        tag = re.sub(r"https://movie.douban.com/tag/","",tag)

        for sel in response.xpath('//div[@class="pl2"]'):
            name = sel.xpath('a//text()').extract()
            Movie_Name = ''.join([re.sub('[ \\n]','',n) for n in name])

            Url = sel.xpath('a/@href').extract()[0]

            Rating_nums = sel.xpath('div/span[@class="rating_nums"]/text()').extract()
            if len(Rating_nums) == 0:
                Rating_nums = ''
            else:
                Rating_nums = Rating_nums[0]

            Comment_nums = re.findall(r'(\w*[0-9]+)\w*',sel.xpath('div/span[@class="pl"]/text()').extract()[0])
            if len(Comment_nums) == 0:
                Comment_nums = 0
            else:
                Comment_nums = Comment_nums[0]

            items = DoubanMovieItem()
            items['Tag'] = tag
            items['Movie_Name'] = Movie_Name
            items['Url'] = Url
            items['Rating_nums'] = Rating_nums
            items['Comment_nums'] = Comment_nums
            yield items
        

        # 实现翻页
        next_url = response.xpath('//div[@class="paginator"]/span[@class="next"]/a/@href').extract()
        if len(next_url) == 0:
            pass
        else:
            next_url = next_url[0]
            print(urllib.request.unquote(next_url))
            yield Request(next_url, callback=self.parse, headers=self.headers)

