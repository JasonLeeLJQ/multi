# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


# class MultiTestPipeline(object):
#     def process_item(self, item, spider):
#         return item

import json
import codecs

import MySQLdb  #MySQL数据库
import MySQLdb.cursors
import logging  #日志

from twisted.enterprise import adbapi

from scrapy import signals
from openpyxl import Workbook  #excel专用

from scrapy.exceptions import DropItem   #用于item不符合要求时，提供报错信息



class QcwyJsonPipeline(object):
    wb = Workbook()  #创建工作簿,同时页建一个sheet
    ws = wb.active
    ws.append(['主键', '职位名称', '详情链接', '公司名称', '薪资(千/月)', '更新时间', '薪资范围','招聘人数','父链接'])  # 设置表头


    def process_item(self, item, spider):  # 工序具体内容

        salary_tmp = item['salary']   #去除千/月的后缀，只保留数字；统一将薪资设置成"千/月"
        if salary_tmp.find(r'千/月') != -1:
            index = salary_tmp.find(r'千/月')
            tmp = salary_tmp[0:index]
            item['salary'] = tmp
        elif salary_tmp.find(r'万/月') != -1:
            index = salary_tmp.find(r'万/月')
            tmp = salary_tmp[0:index]
            salary_list = tmp.split('-')  #对“2-3”进行分割，转换成"千/月"
            if len(salary_list) == 2:
                salary_list[0] = float(salary_list[0]) * 10
                salary_list[1] = float(salary_list[1]) * 10
                result = str(salary_list[0]) + '-' + str(salary_list[1])
                item['salary'] = result
            else:
                raise DropItem("薪资获取不全，不符合‘5-6万/月’的格式 in %s" % item)
        elif salary_tmp.find(r'万/年') != -1:
            index = salary_tmp.find(r'万/年')
            tmp = salary_tmp[0:index]
            salary_list = tmp.split('-')  # 对“2-3”进行分割，转换成"千/月"
            if len(salary_list) == 2:
                salary_list[0] = round(float(salary_list[0]) / 12 * 10,2)  #round小数点之后保留两位
                salary_list[1] = round(float(salary_list[1]) / 12 * 10,2)
                result = str(salary_list[0]) + '-' + str(salary_list[1])
                item['salary'] = result
            else:
                raise DropItem("薪资获取不全，不符合‘5-6万/年’的格式 in %s" % item)
        else:
            raise DropItem("薪资格式不正确，不存在'千/月'、'万/月'、'万/年' in %s" % item)

        line = [item['key'], item['title'], item['link'], item['company'], item['salary'], item['updatetime'],
                item['salary_range'],item['num'],item['parent_link']]  # 把数据中每一项整理出来
        self.ws.append(line)  # 将数据以行的形式添加到xlsx中
        self.wb.save('./test1.xlsx')  # 保存xlsx文件
        return item

class ReadingPipeline(object):
    # def __init__(self):
    #     self.items = []
    def process_item(self, item, spider):
        return item