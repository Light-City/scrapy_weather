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