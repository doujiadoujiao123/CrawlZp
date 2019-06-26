import json
import re
import requests
import time
import multiprocessing
import random
import datetime
from lxml import etree
from selenium import webdriver
from pipline import lg_item
from tools import write_sql
from selenium.webdriver.chrome.options import Options
# from handle_mongo import lagou_mongo


class HandleLaGou(object):

    def __init__(self):
        self.lagou_session = requests.session()
        self.header = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Referer': 'https://www.lagou.com/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        }
        self.city_list = ""
        self.detail_list = []
        self.a = 0
        self.b = 0
        self.c = 0
        self.task_detail_num = 0

    def get_detail_item(self):
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(chrome_options=options)
        for x in range(len(self.detail_list)):
            detail_url = 'https://www.lagou.com/jobs/{}.html'.format(self.detail_list[x]['positionId'])
            try:
                driver.get(detail_url)
                time.sleep(random.randint(5, 8))

                html = etree.HTML(driver.page_source)
                item_dict = lg_item(html, self.detail_list[x])

                # 这里我做的接口入库，代码中并未展示，可以注释一下代码
                res = write_sql.res_post_sql(item_dict)
                print(res)
                print(json.dumps(item_dict))
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
        driver.close()

    def handle_city(self):
        city_search = re.compile(r'zhaopin/">(.*?)</a>')
        city_url = "https://www.lagou.com/jobs/allCity.html"
        city_result = self.handle_request(method='GET',url=city_url)
        self.city_list = city_search.findall(city_result)
        # 清除cookie
        self.lagou_session.cookies.clear()

    def handle_city_job(self,city):
        job_index_url = "https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput="
        self.handle_request(method='GET', url=job_index_url)
        # 页面的url 是post 请求
        page_url = "https://www.lagou.com/jobs/positionAjax.json?city=%s&needAddtionalResult=false"%city
        a = 1
        for page in range(1, 31):
            print('共30页，当前任务池中有任务{}，正在获取第{}页爬虫任务中......'.format(len(self.detail_list), a))
            data = {
                "first": "false",
                "pn": str(page),
                "kd": "动画",
            }
            # 加上请求的域名
            self.header['Referer'] = job_index_url
            job_result = self.handle_request(method='POST',url=page_url,data=data)
            # json.loads 解析 json
            lagou_data = json.loads(job_result)
            # 拿到 14个字典的列表
            job_list = lagou_data['content']['positionResult']['result']
            if job_list:
                for job in job_list:
                    job_item_dict = {}
                    job_item_dict['positionId'] = job['positionId']
                    job_item_dict['district'] = job['district']
                    job_item_dict['skillLables'] = job['skillLables']
                    job_item_dict['createTime'] = job['createTime']
                    # print(json.dumps(job_item_dict))
                    self.detail_list.append(job_item_dict)
                    # lagou_mongo.handle_save_data(job)
                # 爬完一页就停10s ，防封ip
                time.sleep(10)
            else:
                break

    def handle_request(self,method,url,data=None):
        while True:
            try:
                if method == "GET":
                    # response = self.lagou_session.get(url=url,headers=self.header,proxies=proxies)
                    response = self.lagou_session.get(url=url,headers=self.header)
                elif method == "POST":
                    # response = self.lagou_session.post(url=url,headers=self.header,data=data,proxies=proxies,timeout=3)
                    response = self.lagou_session.post(url=url,headers=self.header,data=data)
            except Exception as e:
                print(e)
                continue
            else:
                if '您操作太频繁,请稍后再访问' in response.text:
                    print('频繁')
                    # time.sleep(random.choice(range(5,16)))
                    continue
                elif '爬虫行为' in response.text:
                    print('爬虫')
                    # time.sleep(random.choice(range(5,16)))
                    continue
                else:
                    return response.text

    def run(self):
        # 得到全部城市
        # self.handle_city()
        # for city in self.city_list:
        start = time.time()
        date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start))
        self.handle_city_job('全国')
        self.task_detail_num += len(self.detail_list)
        print("总任务{}".format(len(self.detail_list)))
        self.get_detail_item()

        end_time = time.time()
        result = {
            '开始时间': date,
            '总计用时': start - end_time,
            '总页数': '',
            '总任务': len(self.detail_list),
            '详情任务': self.task_detail_num,
            '上传成功': self.a,
            '上传失败': self.b + self.c,
            '失败': self.b,
            '请求失败': self.c
        }
        print(result)
        print('*********************************************************************************')
        # 开线程池
        # pool = multiprocessing.Pool()
        # pool.apply_async(self.handle_city_job, args=('全国',))
        # pool.close()
        # pool.join()

    def time_run(self, h=1, m=30):
        while True:
            now = datetime.datetime.now()
            if now.hour == h and now.minute == m:
                self.run()
            time.sleep(60)


if __name__ == '__main__':
    lagou = HandleLaGou()
    lagou.time_run()
