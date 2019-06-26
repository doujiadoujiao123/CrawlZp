# -*- coding: utf-8 -*-
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
import requests
from urllib.parse import urljoin
import time, random
import json
import datetime
from urllib.parse import quote, unquote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import etree
from pipline import boss_item
from tools import write_sql


class BossSpider():

    def __init__(self):
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        }
        self.detail_list = []
        self.a = 0
        self.b = 0
        self.c = 0
        self.task_detail_num = 0

    def get_detail_item(self):
        for x in range(len(self.detail_list)):
            detail_url = self.detail_list[x]['detail_url']
            try:
                self.driver.get(self.detail_list[x]['detail_url'])
                # time.sleep(random.randint(5, 8))
                # time.sleep(random.randint(1, 2))
                time.sleep(0.1)

                html = etree.HTML(self.driver.page_source)
                if html.xpath('//h3[@class="gray"]/text()'):
                    self.c += 1
                    print('详情页ip失效')
                    break
                item_dict = boss_item(html, self.detail_list[x])
                item_dict['for_id'] = detail_url.split('.html')[0].split('/')[-1]
                print(json.dumps(item_dict))

                # 这里我做的接口入库，代码中并未展示，可以注释一下代码
                res = write_sql.res_post_sql(item_dict)
                print(res)
                json_data = json.loads(res)
                message = json_data['message']
                if message == '添加成功!':
                    self.a += 1
                elif message == '添加失败!':
                    self.b += 1
                elif message == '参数不完整!':
                    self.b += 1
                else:
                    self.b += 1
            except Exception as e:
                self.c += 1
                print('错误：', e, detail_url)

    def get_list_selenium(self, city, url_str):
        for page in range(1, 11):
            url = 'https://www.zhipin.com/job_detail/?query={}&city={}&page={}'.format(url_str, city['code'], page)
            self.driver.get(url)
            # time.sleep(random.randint(5, 8))
            time.sleep(random.randint(1, 2))
            html = etree.HTML(self.driver.page_source)
            if not html.xpath("//div[@class='page']/a[@class='next']"):
                if html.xpath('//h3[@class="gray"]/text()'):
                    self.c += 1
                    print('详情页ip失效')
                    break
                else:
                    break

            job_list = html.xpath("//div[@class='job-list']/ul/li")
            a = 0
            for x in range(len(job_list)):
                info = {}
                info['job_title'] = job_list[x].xpath(".//div[@class='job-title']/text()")[0]
                if '实习' in info['job_title']:
                    continue
                info['price'] = job_list[x].xpath(".//span[@class='red']/text()")[0]
                describe_1 = job_list[x].xpath("//div[@class='info-primary']/p/text()")
                describe = describe_1[a: a + 3]
                a += 3
                info['location'] = describe_1[0] if len(describe) == 3 else ''
                info['working_life'] = describe_1[1] if len(describe) == 3 else ''
                info['education'] = describe_1[2] if len(describe) == 3 else ''
                info['company_name'] = job_list[x].xpath(".//div[@class='info-company']//h3[@class='name']/a/text()")[0]
                describe_2 = job_list[x].xpath(".//div[@class='info-company']//p/text()")
                info['company_type'] = describe_2[0]
                info['detail_url'] = urljoin("https://www.zhipin.com", job_list[x].xpath(".//h3/a/@href")[0])
                info['city'] = city['name']
                self.detail_list.append(info)

    def handle_city(self):
        city_list = []
        city_api_url = "https://www.zhipin.com/wapi/zpCommon/data/city.json"
        city_response = requests.get(url=city_api_url, headers=self.headers)
        for province in json.loads(city_response.text)['zpData']['cityList']:
            for city in province['subLevelModelList']:
                city_list.append(city)
        return city_list

    def run(self):
        start = time.time()
        date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start))

        str_key = '动画'
        url_str = quote(str_key)
        city_list = self.handle_city()
        a = 0
        for city in city_list:
            a += 1
            self.get_list_selenium(city, url_str)
            # time.sleep(random.randint(5, 8))
            print('第{}个城市:{},城市ID:{},任务数:{}.'.format(a, city['name'], city['code'], len(self.detail_list)))
            self.task_detail_num += len(self.detail_list)

            self.get_detail_item()
            self.detail_list.clear()
            # time.sleep(random.randint(5, 8))
        self.driver.close()

        end_time = time.time()
        result = {
            '开始时间': date,
            '总计用时': start - end_time,
            '总页数': '',
            '总任务': len(city_list),
            '详情任务': self.task_detail_num,
            '上传成功': self.a,
            '上传失败': self.b + self.c,
            '失败': self.b,
            '请求失败': self.c
        }
        print(result)

    def time_run(self, h=1, m=30):
        while True:
            now = datetime.datetime.now()
            if now.hour == h and now.minute == m:
                self.run()
            time.sleep(60)


if __name__ == '__main__':
    boss = BossSpider()
    boss.time_run()
