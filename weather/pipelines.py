# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os,json

import pymongo
import pymysql

import requests
from scrapy import Request
pathdir = os.getcwd()
class WeatherPipeline(object):
    def process_item(self, item, spider):
        # 文件存在data目录下的weather.txt文件内
        fiename = pathdir + '\\data\\weather.txt'
        # 从内存以追加的方式打开文件，并写入对应的数据
        with open(fiename, 'a', encoding='utf8') as f:
            for i in range(7):
                f.write('日期:' + item['date'][i] + '\n')
                f.write('星期:' + item['week'][i] + '\n')
                f.write('最高温度:' + item['high_temperature'][i] + '\n')
                f.write('最低温度' + item['low_temperature'][i] + '\n')
                f.write('天气:' + item['weather'][i] + '\n')
                f.write('风况:' + item['wind'][i] + '\n')
                f.write('-------------------------------------' + '\n')

        return item

class W2json(object):
    def process_item(self, item, spider):
        '''
        讲爬取的信息保存到json
        方便调用
        '''
        filename = pathdir + '\\data\\weather.json'

        # 打开json文件，向里面以dumps的方式吸入数据
        # 注意需要有一个参数ensure_ascii=False ，不然数据会直接为utf编码的方式存入比如:“/xe15”
        with open(filename, 'a', encoding='utf8') as f:
            line = json.dumps(dict(item), ensure_ascii=False) + '\n'
            f.write(line)

        return item

class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):

        self.db[item.collection].insert(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()

class W2mysql(object):
    def process_item(self, item, spider):
        '''
        将爬取的信息保存到mysql
        '''

        connection = pymysql.connect(host='localhost', user='root', password='xxx', db='scrapydb',
                                     charset='utf8mb4')
        try:

            with connection.cursor() as cursor:
                for i in range(7):
                    sql = "insert into `weather`(`date`,`week`,`high_temperature`,`low_temperature`,`weather`,`wind`,`img`)values(%s,%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql, (
                        item['date'][i], item['week'][i], item['high_temperature'][i], item['low_temperature'][i],
                        item['weather'][i],
                        item['wind'][i], item['img'][i]))

                connection.commit()
        # except pymysql.err.IntegrityError as e:
        #     print('重复数据，勿再次插入!')
        finally:
            connection.close()

        return item


