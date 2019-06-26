# -*- coding: utf-8 -*-
import json
import requests


async def post_sql(item_dict, session):
    post_url = ''
    async with session.get(url=post_url, data={"data": json.dumps(item_dict)}) as response:
        response_text = await response.text()
        print(response_text)


def res_post_sql(item_dict):
    post_url = ''
    res = requests.post(url=post_url, data={"data": json.dumps(item_dict)})
    return res.text


def vitae_res_post_sql(item_dict):
    post_url = ''
    res = requests.post(url=post_url, data={"data": json.dumps(item_dict)})
    return res.text
