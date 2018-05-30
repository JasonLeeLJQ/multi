#coding=utf-8

'''
爬虫程序的父类

'''
import scrapy

class fatherclass(scrapy.Spider):
    # 获取url
    def start_requests(self):
        pass

    # 对response进行HTML结构分析
    def parse(self,response):
        pass