# -*- coding: utf-8 -*-
import time, datetime
from datetime import datetime
import json
from tools import tools_class
from lxml import etree

item_dict = {
    'img': '',
    'name': '',
    'province': '',
    'city': None,
    'area': None,
    'address': '',
    'num': 0,
    'salary_start': 0,
    'salary_end': 0,
    'intro': '',
    'working_year': '',
    'education': '',
    'age': None,
    'company_intro': None,
    'company_name': '',
    'publish_time': None,
    'end_time': None,
    'walfares': '',
    'skills': '',
}


def boss_item(html, detail_list):
    price = detail_list['price']
    location = detail_list['location']
    name = detail_list['job_title']
    company_name = detail_list['company_name']
    education = detail_list['education']
    working_year = detail_list['working_life']
    salary_start = int(float(price.split('-')[0]) * 1000) if 'K' in price and '-' in price else 0
    salary_end = int(float(price.split('-')[1].split('K')[0]) * 1000) if 'K' in price and '-' in price else 0
    city = detail_list['city'] + '市'
    area = location.split(' ')[1] if location != '' else None

    img_xpath = html.xpath('//div[@class="company-info"]/a[1]/img/@src')
    address_xpath = html.xpath('//div[@class="location-address"]/text()')
    intro_xpath = html.xpath('//div[@class="job-sec"]/div[@class="text"]//text()')
    company_intro_xpath = html.xpath('//div[@class="job-sec company-info"]/div//text()')
    walfares_xpath_1 = html.xpath('//div[@class="job-tags"][1]/span/text()')
    walfares_xpath = list(set(walfares_xpath_1))

    item_dict['img'] = img_xpath[0] if len(img_xpath) != 0 else ''
    item_dict['address'] = address_xpath[0] if len(address_xpath) != 0 else ''
    item_dict['num'] = 0
    item_dict['province'] = ''
    item_dict['intro'] = ','.join(intro_xpath).replace(',', '').strip() if len(intro_xpath) != 0 else ''
    item_dict['age'] = '年龄不限'
    item_dict['company_intro'] = ','.join(company_intro_xpath).replace(',', '').strip() if len(company_intro_xpath) != 0 else None
    item_dict['publish_time'] = None
    item_dict['end_time'] = None
    item_dict['walfares'] = ','.join(walfares_xpath) if len(walfares_xpath) != 0 else ''
    item_dict['skills'] = ''
    item_dict['source'] = 6
    item_dict['name'] = name
    item_dict['company_name'] = company_name
    item_dict['education'] = education
    item_dict['working_year'] = working_year
    item_dict['salary_start'] = salary_start
    item_dict['salary_end'] = salary_end
    item_dict['city'] = city
    item_dict['area'] = area
    return item_dict


def cs_boss_item(html):

    img_xpath = html.xpath('//div[@class="company-info"]/a[1]/img/@src')
    address_xpath = html.xpath('//div[@class="location-address"]/text()')
    intro_xpath = html.xpath('//div[@class="job-sec"]/div[@class="text"]//text()')
    company_intro_xpath = html.xpath('//div[@class="job-sec company-info"]/div//text()')
    walfares_xpath_1 = html.xpath('//div[@class="job-tags"][1]/span/text()')
    walfares_xpath = list(set(walfares_xpath_1))

    item_dict['img'] = img_xpath[0] if len(img_xpath) != 0 else ''
    item_dict['address'] = address_xpath[0] if len(address_xpath) != 0 else ''
    item_dict['num'] = 0
    item_dict['province'] = ''
    item_dict['intro'] = ','.join(intro_xpath).replace(',', '').strip() if len(intro_xpath) != 0 else ''
    item_dict['age'] = '年龄不限'
    item_dict['company_intro'] = ','.join(company_intro_xpath).replace(',', '').strip() if len(company_intro_xpath) != 0 else None
    item_dict['publish_time'] = None
    item_dict['end_time'] = None
    item_dict['walfares'] = ','.join(walfares_xpath) if len(walfares_xpath) != 0 else ''
    item_dict['skills'] = ''
    item_dict['source'] = 6
    return item_dict


def lg_item(html, detail_dict):
    area = detail_dict['district']
    skills = detail_dict['skillLables']
    positionId = detail_dict['positionId']
    createTime = detail_dict['createTime']
    local_timestamp = tools_class.lg_date1(createTime)

    img_xpath = html.xpath('//dl[@class="job_company"]/dt/a/img/@src')
    name_xpath = html.xpath('//div[@class="job-name"]/span[@class="name"]/text()')
    city_xpath = html.xpath('//dd[@class="job_request"]/p/span[2]/text()')
    address_xpath = html.xpath('//div[@class="work_addr"]//text()')
    address_str = ','.join(address_xpath).replace(',', '').replace(' ', '').replace('\n', '').replace('查看地图', '') \
        if len(address_xpath) != 0 else ''

    salary_start_1 = html.xpath('//dd[@class="job_request"]/p/span[1]/text()')[0]
    salary_start = salary_start_1 if len(salary_start_1) != 0 else 0
    salary_1 = int(float(salary_start.split('-')[0].split('k')[0]) * 1000) if 'k' in salary_start and '-' in salary_start else 0
    salary_2 = int(float(salary_start.split('-')[1].split('k')[0]) * 1000) if 'k' in salary_start and '-' in salary_start else 0

    intro_xpath = html.xpath('//dd[@class="job_bt"]/div[@class="job-detail"]/p/text()')
    working_year_xpath = html.xpath('//dd[@class="job_request"]/p/span[3]/text()')
    education_xpath = html.xpath('//dd[@class="job_request"]/p/span[4]/text()')
    company_name_xpath = html.xpath('//div[@class="job_company_content"]/h2/em/text()')

    publish_time_xpath = html.xpath('//p[@class="publish_time"]/text()')
    # local_timestamp = tools_class.lg_date(publish_time_xpath)

    walfares_xpath = html.xpath('//dd[@class="job-advantage"]/p/text()')

    item_dict['img'] = 'https:' + img_xpath[0] if len(img_xpath) != 0 else ''
    item_dict['name'] = name_xpath[0] if len(name_xpath) != 0 else ''
    item_dict['province'] = ''
    item_dict['city'] = city_xpath[0].replace('/', '').strip() + '市' if len(city_xpath) != 0 else ''
    item_dict['area'] = area if area != '' else None
    item_dict['address'] = address_str
    item_dict['num'] = 0
    item_dict['salary_start'] = salary_1
    item_dict['salary_end'] = salary_2
    item_dict['intro'] = ','.join(intro_xpath).replace(',', '') if len(intro_xpath) != 0 else ''
    item_dict['working_year'] = working_year_xpath[0].replace('/', '').strip() if len(working_year_xpath) != 0 else ''
    item_dict['education'] = education_xpath[0].replace('/', '').strip() if len(education_xpath) != 0 else ''
    item_dict['age'] = None
    item_dict['company_intro'] = None
    item_dict['company_name'] = company_name_xpath[0].strip() if len(company_name_xpath) != 0 else ''
    item_dict['publish_time'] = local_timestamp
    item_dict['end_time'] = None
    item_dict['walfares'] = ','.join(walfares_xpath) if len(walfares_xpath) != 0 else ''
    item_dict['skills'] = ','.join(skills) if len(skills) != 0 else ''
    item_dict['source'] = 3
    item_dict['for_id'] = '{}'.format(positionId)
    return item_dict


