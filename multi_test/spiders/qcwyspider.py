# -*- coding: utf-8 -*-
'''
最新版qcwy
version 2.0
@Jason & Fairy
'''
import logging
import scrapy
import urllib
import codecs
import os
import random  #生成一个随机数
import re

from scrapy.selector import Selector
from scrapy.http import Request

from urllib import urlencode  #2.7版本
# from urllib.parse import urlencode  #3.5版本

from multi_test.items import QcwyItem

from scrapy.exceptions import DropItem   #用于item不符合要求时，提供报错信息

import fatherspider  # 导入父类fatherclass


import sys

reload(sys)
sys.setdefaultencoding('utf-8')

# keyword = "Python"
# # 把字符串编码成符合url规范的编码
# keywordcode = urllib.quote(keyword)

#正则表达式
mode = re.compile(r'\d+')

# class TestfollowSpider(scrapy.Spider):
class TestfollowSpider(fatherspider.fatherclass):
    name = "qcwysearch"
    allowed_domains = ["51job.com"]
    start_urls = [
        'https://search.51job.com/list/180200,000000,2402,37,9,99,DSP,2,1.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=',
    ]

    #自定义start_urls,原先的start_urls列表失效
    def start_requests(self):
        #需要POST的参数
        paras = {
            'lang': 'c',
            'stype': '',
            'postchannel': '0000',
            'workyear': 99,
            'cotype': 99,
            'degreefrom': 99,
            'jobterm': 99,
            'companysize': 99,
            'providesalary': 99,
            'lonlat': '0,0',
            'radius': -1,
            'ord_field': 0,
            'confirmdate': 9,
            'fromType': '',
            'dibiaoid': 0,
            'address': '',
            'line': '',
            'specialarea': '00',
            'from': '',
            'welfare': ''
        }
        # #请求的头部
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.18 Safari/537.36',
        #     'Referer': 'https://search.51job.com/',
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        #     'Accept-Encoding': 'gzip, deflate, br',
        #     'Accept-Language': 'zh-CN,zh;q=0.9'
        # }
        '''
        keyword:         Python (7st)
        city:            180200 (1st)
        profession:      01     (4st)
        career:          2607   (3rd)
        '''
        #必须首先判断当前路径下，是否存在weblist.txt文件
        if os.path.exists('./weblist1.txt'):
            print('自定义start_url开始执行')
            #读取网址，分析网址，去除需要的元素,需要将网址复制到当前目录下的./weblist.txt中
            with open('./weblist1.txt', 'r') as f:
                line = f.readline()
                while line:
                    tmp = line.split('/')[-1]
                    res = tmp.split(',')[:7]    #res是一个list
                    print(res)

                    keyword     = res[-1]
                    city        = res[0]
                    profession  = res[3]
                    career      = res[2]

                    with open('./result_web.txt','a+') as file:
                        parent_link = keyword+'/'+city+'/'+profession+'/'+career
                        file.write(parent_link+'\n')

                    url = 'https://search.51job.com/list/' + city + ',000000,' + career + ',' + profession + ',' + '9,99,' + keyword + ',' + '2,1.html?' + urlencode(paras)
                    print(url)

                    # 将获取的链接封装成request请求，传给schedule
                    request = Request(url, callback=self.parse)
                    request.meta['parent_link'] = parent_link
                    yield request

                    line = f.readline()
        else:
            print('当前路径下不存在weblist.txt文件，必须手动添加才可以进行爬取操作！')

    # 对某一个具体行业的一个职位进行爬取
    def parse(self,response):
        sel = scrapy.selector.Selector(response)
        #/ html / body / div[2] / div[1] / div[3] / ul
        results = sel.xpath('//html/body/div[@class="dw_wp"]/div[@class="dw_filter dw_filter"]/div[@id="filter_providesalary" and @class="el mk"]/ul/li/a[not(@class="dw_c_orange")]')

        #对于每一个父链接，都存在一个dict，保存不同薪资区间的人数
        # tmp_dict = dict()
        # print(results.extract())
        for result in results:
            tmp_url = result.xpath('@href').extract()[0].encode('utf-8')  #链接
            salary_range = result.xpath('text()').extract()[0].encode('utf-8')  #薪水范围

            # tmp_dict[salary_range] = int(0)
            # print(tmp)
            # print(salary_range)
            #将获取的链接封装成request请求，传给schedule
            request = Request(tmp_url, callback=self.parse_range)
            request.meta['salary_range'] = salary_range
            request.meta['parent_link']  = response.meta['parent_link']
            # request.meta['tmp_dict']     = tmp_dict
            yield request

    # 月薪范围不同，对单个月薪范围进行统计
    def parse_range(self, response):

        sel = scrapy.selector.Selector(response)

        sites = sel.xpath('//body/div[@class="dw_wp"]/div[@id="resultList" and @class="dw_table"]/div[@class="el"]')
        # href = response.xpath('//body/div[@class="dw_wp"]/div[@id="resultList" and @class="dw_table"]')
        # url = response.urljoin(href.extract())
        # print(url)

        for site in sites:
            item = QcwyItem()

            #/ html / body / div[2] / div[4] / div[4] / p / span / a
            a = site.xpath('p/span/a/@title').extract()
            # print(type(a))
            '''
            之前显示的是ascii字符，将其编码成utf8字符进行显示
            '''
            item['title'] = a[0].encode('utf-8')

            b = site.xpath('p/span/a/@href').extract()
            item['link'] = b[0].encode('utf-8')

            c = site.xpath('span[@class="t2"]/a/@title').extract()
            item['company'] = c[0].encode('utf-8')

            d = site.xpath('span[@class="t4"]/text()').extract()
            item['salary'] = d[0].encode('utf-8')

            e = site.xpath('span[@class="t5"]/text()').extract()
            item['updatetime'] = e[0].encode('utf-8')

            # 薪资范围直接从response中获取即可,get the parameter from the response
            item['salary_range'] = response.meta['salary_range']

            #父链接
            item['parent_link'] = response.meta['parent_link']

            #获取数据库的主键
            item['key'] = item['parent_link'] + '/' + str(random.randint(0,10000))
            # 将获取的链接封装成request请求，传给schedule
            request = Request(item['link'], callback=self.parse_contents)
            request.meta['total_item'] = item
            # request.meta['tmp_dict']   = response.meta['tmp_dict']
            yield request
        # yield scrapy.Request(url, callback=self.parse_dir_contents)

    #进入企业的详细链接，获取招聘人数
    def parse_contents(self, response):
        item = response.meta['total_item']  #获取上一个函数传递过来的参数
        # tmp_dict = response.meta['tmp_dict']

        sel = scrapy.selector.Selector(response)
        #/ html / body / div[3] / div[2] / div[3] / div[1] / div / div / span[3]
        #需要注意的是：招聘人数在<em class="i3">标签下，所以先获取em标签，在获取em标签的父节点的text文本。
        site = sel.xpath('// html/body/div[3]/div[2]/div[3]/div[1]/div/div/span[3]/em[@class="i3"]/parent::span/text()').extract()
        # print site
        if len(site) != 0:    #没有招聘人数的就剔除
            # item['num'] = site[0].encode('utf-8')
            # print(type(item['num']))

            tmp = site[0].encode('utf-8')
            res = mode.findall(tmp)
            if len(res) != 0:
                item['num'] = int(res[0])

                #对应薪资区间招聘人数+1
                # tmp_dict[item['salary_range']] += 1
                #加入到statistic_salary统计字典中
                # statistic_salary[item['parent_link']] = tmp_dict

                yield item
            else:
                item['num'] = 0
                raise DropItem("没有指定具体人数 in %s" % item)