#!/usr/bin/env python
#coding=utf-8
import commands
print('启动爬虫程序qcwysearch')
dir1 = commands.getstatusoutput('scrapy crawl qcwysearch')
# print(dir)
if isinstance(dir1[0],int) and dir1[0] == 0:
	print('爬虫程序qcwysearch爬取数据成功！')
else:
	print('爬虫程序qcwysearch爬取数据失败！')
	print(dir1[1])

print('启动爬虫程序read')
dir2 = commands.getstatusoutput('scrapy crawl read')
# print(dir)
if isinstance(dir2[0],int) and dir2[0] == 0:
	print('爬虫程序read爬取数据成功！')
else:
	print('爬虫程序read爬取数据失败！')
	print(dir2[1])

