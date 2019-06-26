# -*- coding: utf-8 -*-
import time
from datetime import datetime
from pandas.tseries.offsets import Day


# arr是被分割的list，n是每个chunk中含n元素。
def chunks(arr, n):
    return [arr[i:i + n] for i in range(0, len(arr), n)]


def lg_date(publish_time_xpath):
    local_timestamp = None
    if len(publish_time_xpath) == 0:
        pass

    else:
        date = publish_time_xpath[0]
        if '-' in date:
            crate_date = date.split('发布')[0].strip() + ' 00:00:00.000'
            local_datetime = datetime.strptime(crate_date, "%Y-%m-%d %H:%M:%S.%f")
            local_timestamp = int(
                time.mktime(local_datetime.timetuple()) * 1000.0 + local_datetime.microsecond / 1000.0)

        elif '天' in date:
            int_data = int(date.split('天')[0].strip())
            now_time = datetime.now()  # 获取当前时间
            yes_time = (now_time - int_data * Day()).strftime('%Y-%m-%d')  # 格式化
            # 不知为啥lxml.etree没有 today 错误
            # yesterday = (date.today() + timedelta(days=-a)).strftime("%Y-%m-%d")
            crate_date = yes_time + ' 00:00:00.000'
            local_datetime = datetime.strptime(crate_date, "%Y-%m-%d %H:%M:%S.%f")
            local_timestamp = int(
                time.mktime(local_datetime.timetuple()) * 1000.0 + local_datetime.microsecond / 1000.0)

        elif ':' in date:
            crate_date = datetime.now().strftime('%Y-%m-%d') + ' 00:00:00.000'
            local_datetime = datetime.strptime(crate_date, "%Y-%m-%d %H:%M:%S.%f")
            local_timestamp = int(
                time.mktime(local_datetime.timetuple()) * 1000.0 + local_datetime.microsecond / 1000.0)
        else:
            pass
    return local_timestamp


def lg_date1(publish_time_xpath):
    crate_date = publish_time_xpath + '.000'
    local_datetime = datetime.strptime(crate_date, "%Y-%m-%d %H:%M:%S.%f")
    local_timestamp = int(
        time.mktime(local_datetime.timetuple()) * 1000.0 + local_datetime.microsecond / 1000.0)
    return local_timestamp




