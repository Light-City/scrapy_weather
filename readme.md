---
title: Scrapy框架之爬取城市天气预报
tags: 爬虫系列
categories: Python
abbrlink:
date: 2018-08-27 13:56:09
---

![](http://p20tr36iw.bkt.clouddn.com/py_scrapy_mongodb.png)

<!--more-->

# Scrapy框架之爬取城市天气预报

## 1.项目初始化

- 创建项目

```python
scrapy startproject weather
```
- 创建Spider

```python
scrapy genspider CqtianqiSpider tianqi.com
'''
由于CqtianqiSpider这个名字在后面scrapy crawl CqtianqiSpider中,
CqtianqiSpider名字太长,将spider中的name改为CQtianqi,
然后命令变为：scrapy crawl CQtianqi
'''
```

## 2.提取数据


### 2.1 数据分析

![](http://p20tr36iw.bkt.clouddn.com/py_scrapy_weath_pre.png)

这次目的是抽取重庆及盐湖区7日天气预报,具体源码情况如上图所示，截出的就是本次爬虫所需要定位的地方。

接下来，定义以下存储的数据!

```
date = 当日日期
week = 星期几
img = 当日天气图标
wind = 当日风况
weather = 当日天气
high_temperature = 当日最高温度
low_temperature = 当日最低温度
```

### 2.2 数据抽取

修改`items.py`

```python
import scrapy
class WeatherItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    collection = 'weather'
    date = scrapy.Field()
    week = scrapy.Field()
    img = scrapy.Field()
    high_temperature = scrapy.Field()
    low_temperature = scrapy.Field()
    weather = scrapy.Field()
    wind = scrapy.Field()
```

### 2.3 自定义spider

`CQtianqi.py`

```python
# -*- coding: utf-8 -*-
import scrapy
from weather.items import WeatherItem
class CqtianqiSpider(scrapy.Spider):
    name = 'CQtianqi'
    allowed_domains = ['tianqi.com']
    start_urls = []
    citys = ['chongqing','yanhuqu']
    for city in citys:
        start_urls.append('http://'  + 'www.tianqi.com/' + city + '/')
    def parse(self, response):
        '''
        date = 当日日期
        week = 星期几
        img = 当日天气图标
        wind = 当日风况
        weather = 当日天气
        high_temperature = 当日最高温度
        low_temperature = 当日最低温度
        :param response:
        :return:
        '''
        # oneweek = response.xpath('//div[@class="day7"]')
        item = WeatherItem()
        date = response.xpath('//div[@class="day7"]//ul[@class="week"]//li//b/text()').extract()
        week = response.xpath('//div[@class="day7"]//ul[@class="week"]//li//span/text()').extract()
        base_url = 'https://www.tianqi.com'
        img = response.xpath('//div[@class="day7"]//ul[@class="week"]//li//img/@src').extract()
        imgs = []
        for i in range(7):
            img_i = img[i]
            img_url = base_url + img_i
            imgs.append(img_url)

        print(date)
        print(week)
        print(imgs)
        weather = response.xpath('//div[@class="day7"]//ul[@class="txt txt2"]//li/text()').extract()

        print(weather)
        high_temperature = response.xpath('//div[@class="day7"]//div[@class="zxt_shuju"]/ul//li/span/text()').extract()
        low_temperature = response.xpath('//div[@class="day7"]//div[@class="zxt_shuju"]/ul//li/b/text()').extract()
        print(high_temperature)
        print(low_temperature)

        wind = response.xpath('//div[@class="day7"]//ul[@class="txt"][1]//li/text()').extract()
        print(wind)

        item['date'] = date
        item['week'] = week
        item['img'] = imgs
        item['weather'] = weather
        item['wind'] = wind
        item['high_temperature'] = high_temperature
        item['low_temperature'] = low_temperature
        yield item  
```

## 3.存储数据

### 3.1 修改`settings.py`

```python
# 这两行直接添加
MONGO_URI = 'localhost'
MONGO_DB = 'test'
# 以下直接修改
ITEM_PIPELINES = {
   'weather.pipelines.WeatherPipeline': 300,
   'weather.pipelines.W2json': 301,
   'weather.pipelines.MongoPipeline': 302,
   'weather.pipelines.W2mysql': 303,
}
ROBOTSTXT_OBEY = False
USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Mobile Safari/537.36'

```

### 3.2 数据存储


修改`pipelines.py`

```python
import os,json
import pymongo
import pymysql
import requests
from scrapy import Request

class WeatherPipeline(object):
    def process_item(self, item, spider):
        # 获取当前工作目录
        base_dir = os.getcwd()
        # 文件存在data目录下的weather.txt文件内
        fiename = base_dir + '\\data\\weather.txt'
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

        # 下载图片
        for i in range(7):
            url = item['img'][i]
            file_name = url.split('/')[-1]
            with open(base_dir + '\\data\\' + file_name, 'wb') as f:
                f.write(requests.get(url).content)
        return item

class W2json(object):
    def process_item(self, item, spider):
        '''
        讲爬取的信息保存到json
        方便调用
        '''
        base_dir = os.getcwd()
        filename = base_dir + '/data/weather.json'

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
        connection = pymysql.connect(host='localhost', user='root', password='xxxxxx', db='scrapydb',
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
```

- 图片下载到本地

爬取的是两个地方的天气预报，每个有7张，总共14张图片，因为我在存储的时候以图片地址末尾的xx.png命名，那么在写的时候由于有些重复了，所以只有这几张图片。

![](http://p20tr36iw.bkt.clouddn.com/py_img.png)

- 数据存储至txt

这里只截了一部分数据，实际每个重复两次。

![](http://p20tr36iw.bkt.clouddn.com/py_txt.png)

- 数据存储至json

这个不是重复，存储的是两个地区数据！

![](http://p20tr36iw.bkt.clouddn.com/py_json.png)

- 数据存储至MongoDB

这个不是重复，存储的是两个地区数据！
![](http://p20tr36iw.bkt.clouddn.com/py_scrapy_mongodb.png)

- 数据存储至MySql

这个不是重复，存储的是两个地区数据！

![](http://p20tr36iw.bkt.clouddn.com/py_scrapy_mysql.png)

## 4.项目地址

[项目地址戳这里!!!](https://github.com/Light-City/scrapy_weather)
