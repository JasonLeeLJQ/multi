#coding=utf-8

import scrapy
from multi_test.items import ReadingItem
# import urllib.request
import os
import re

from scrapy.http import Request

import fatherspider  # 导入父类fatherclass

class read(fatherspider.fatherclass):
    name = 'read'
    allowed_domains = ['xunsee.com']
    start_urls = ['http://xunsee.com']

    def start_requests(self):
        url = 'http://xunsee.com'
        request = Request(url, callback=self.parse)
        yield request

    def parse(self,response):
        # filename = '1'
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        sel = scrapy.selector.Selector(response)
        sites = sel.xpath('//div[@class="list"]')

        #一个item对象的列表
        # items = []
        for site in sites:
            #构造一个item对象
            item = ReadingItem()

            '''
            get the name of the book
            '''
            a = site.xpath('span[@class="title"]/a/text()').extract()
            item['name_read'] = a[0].encode('utf-8')
            # print(a)
            '''
            get the author of the book
            '''
            b = site.xpath('span[@class="author"]/a/text()').extract()
            item['author_read'] = b[0].encode('utf-8')
            # print(b)
            '''
            get the class of the book
            '''
            c = site.xpath('span[@class="cate"]/text()').extract()
            item['class_read'] = c[0].encode('utf-8')
            # print(c)

            '''
            get the link of the book
            '''
            d = site.xpath('span[@class="title"]/a/@href').extract()
            temp = d[0].encode('utf-8')
            # print(d)

            real_url = self.start_urls[0] + temp
            item['link_read'] = real_url

            '''
            获取每一个item信息之后，就提交给pipeline
            '''
            yield item
            # with open('text','wb+') as file:
            #     file.write(real_url)
        #     items.append(item)
        # return items
            '''
            接下来，对获取的链接进行获取，也就是该小说的总链接
            need pass parameters to the object of Request,we must use Request.meta
            '''
            # yield Request(real_url, callback=self.parse_item)
            request = Request(real_url,callback=self.parse_item)
            request.meta['name_read'] = item['name_read']
            yield request

    '''
    对小说的总链接中的内容进行分析
    即，拆分出每一个章节的链接
    '''
    def parse_item(self,response):
        sel = scrapy.selector.Selector(response)
        sites = sel.xpath('//span[@class="spant"]')

        # get the parameter from the response
        name_read = response.meta['name_read']

        for site in sites:
            a = site.xpath('a/@href').extract()
            # print(a)
            temp_url  = a[0].encode('utf-8')
            charpter_real_url = '/'.join(response.url.split('/')[:-1]) + '/' + temp_url
            # print(charpter_real_url)
            # print(self.item['link_read'])
            # print(response.url)
            # yield Request(charpter_real_url,callback=self.parse_text_item)
            request = Request(charpter_real_url,callback=self.parse_text_item)
            request.meta['name_read'] = name_read
            yield request
    '''
    对每一章节的内容进行crawl
    '''
    def parse_text_item(self,response):
        '''
        取得网页中的小说文本，并将它保存起来
        :param response:
        :return:
        '''
        sel = scrapy.selector.Selector(response)
        sites = sel.xpath('//div[@id="content_1"]/text()')
        # print(response.url)

        # get the parameter from the response
        name_read = response.meta['name_read']

        #网页的地址
        name_text = response.url
        #对网页的地址进行分割，获取章节号
        # different reading has different name_head,
        # name_head = name_text.split('/')[-2][-4:]
        name_text = name_text.split('/')[-1]
        name_text = name_read + '_' + name_text.split('.')[0] + '.txt'
        print(name_text)
        with open('read.txt','a+') as f:
            f.write(name_text)