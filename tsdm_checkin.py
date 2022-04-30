# !/usr/bin/env python3
# -*- encoding: utf-8 -*-
import sys
import time
from urllib.parse import urljoin

import requests
import schedule
import toml
from loguru import logger
from parsel import Selector


def read_config(config_file):
    config = toml.load(config_file)
    os = config.get("os")
    cookies = config.get("cookies")
    url = config.get("url").get("base_url")
    task_loop_minutes = config.get("task").get("minutes")
    message = config.get("message")
    dingding_url, secret = (
        message.get("dingding").values()
        if message.get("dingding").values()
        else [None, None]
    )
    gotify_url = message.get("gotify").get("url")
    if not cookies or not url:
        logger.error("未在配置文件找到用户cookie或者天使动漫网址")
        return
    if dingding_url and secret and gotify_url:
        return {
            "os": os,
            "push_mode": "dingding_and_gotify",
            "cookies": cookies,
            "task_loop_minutes": task_loop_minutes,
            "checkin_url": url,
            "dingding_url": dingding_url,
            "dingding_secret": secret,
            "gotify_url": gotify_url,
        }
    elif dingding_url and secret:
        return {
            "os": os,
            "push_mode": "dingding",
            "cookies": cookies,
            "task_loop_minutes": task_loop_minutes,
            "checkin_url": url,
            "dingding_url": dingding_url,
            "dingding_secret": secret,
        }
    elif gotify_url:
        return {
            "os": os,
            "push_mode": "gotify",
            "cookies": cookies,
            "task_loop_minutes": task_loop_minutes,
            "checkin_url": url,
            "gotify_url": gotify_url,
        }

    else:
        return {
            "os": os,
            "push_mode": None,
            "cookies": cookies,
            "task_loop_minutes": task_loop_minutes,
            "checkin_url": url,
        }


def tsdm_login(cookie):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.36 Safari/537.36 Edg/97.0.1072.28",
        "Cookie": cookie,
    }
    login_url = urljoin(base_url, "forum.php")
    session = requests.Session()
    session.headers = headers
    try:
        login_response = session.get(login_url)
    except Exception as e:
        logger.error(e)
        return
    selector = Selector(text=login_response.text)
    if selector.css("#ls_username") and selector.css("#ls_password"):
        logger.error("cookie已经失效，请重新登录获取cookie")
        return
    return session


def tsdm_work(session):
    work_url = urljoin(base_url, "plugin.php?id=np_cliworkdz:work")
    response = session.get(work_url)
    tips = Selector(text=response.text).xpath('//*[@id="messagetext"]/p[1]/text()')
    if tips:
        # logger.info("打工%s" % "".join(tips.getall()))
        return {"work_info": "打工%s" % "".join(tips.getall()), "work_status": False}
    for n in range(1, 7):
        session.post(work_url, data={"act": "clickad"})
        # logger.info("正在点击第%s广告" % n)
    response = session.post(work_url, data={"act": "getcre"})
    message = "打工完成，%s" % "".join(
        Selector(text=response.text)
        .css("#messagetext.alert_info p")
        .re("<p>(.*?)<br>(.*?)<script")
    )
    return {"work_info": message, "work_status": True}
    # logger.info(message)


def checkin(session):
    checkin_url = urljoin(base_url, "plugin.php?id=dsu_paulsign:sign")
    response = session.get(checkin_url)
    from_hash = (
        Selector(text=response.text).xpath('//*[@id="qiandao"]/input/@value').get()
    )
    if not from_hash:
        return
    checkin_api = urljoin(
        base_url, "plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=1"
    )
    data = {"formhash": from_hash, "qdxq": "ch", "qdmode": 3, "fastreply": 0}
    checkin_response = session.post(checkin_api, data=data)
    return True


def main(config):
    global base_url
    push_mode = config.get("push_mode")
    cookies = config.get("cookies")
    base_url = config.get("checkin_url")
    os = config.get("os")

    def users_checkin(cookies):
        for user, cookie in cookies.items():
            session = tsdm_login(cookie)
            if session:
                checkin_result = checkin(session)
                work_result = tsdm_work(session)
                if checkin_result:
                    logger.info("TSDM 签到成功！")
                if work_result.get("work_status") == True:
                    logger.info(work_result.get("work_info"))

    if push_mode == "dingding" and os == "Linux":
        logger.info("当前推送消息模式为钉钉")
        dingding_url = config.get("dingding_url")
        dingding_secret = config.get("dingding_secret")

        @ding_bot(dingding_url, dingding_secret)
        def dingding_mode():
            users_checkin(cookies)

        dingding_mode()
    elif push_mode == "gotify" and os == "Linux":
        logger.info("当前推送消息模式为gotify")
        gotify_url = config.get("gotify_url")

        @gotify(gotify_url, 1)
        def gotify_mode():
            users_checkin(cookies)

        gotify_mode()
    elif push_mode == "dingding_and_gotify" and os == "Linux":
        logger.info("当前推送消息模式为钉钉和gotify")
        dingding_url = config.get("dingding_url")
        dingding_secret = config.get("dingding_secret")
        gotify_url = config.get("gotify_url")

        @ding_bot(dingding_url, dingding_secret)
        @gotify(gotify_url, 1)
        def dingding_and_gotify_mode():
            users_checkin(cookies)

        dingding_and_gotify_mode()
    else:
        logger.info("没有签到打工消息推送")
        users_checkin(cookies)


if __name__ == "__main__":
    log_config = {
        "handlers": [
            {"sink": sys.stdout, "format": "{time} - {level} - {message}"},
            {"sink": "checkin.log"},
        ],
        "extra": {"user": "someone"},
    }
    logger.configure(**log_config)
    config_file = "config.toml"
    config = read_config(config_file)
    os = config.get("os")
    task_loop_minutes = config.get("task_loop_minutes")
    logger.info(f"当前系统平台为{os}, 每{task_loop_minutes}分钟签到和打工一次")
    if os == "Linux":
        from message_push import *

        main(config)
        schedule.every(task_loop_minutes).minutes.do(main, config)
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        main(config)
        schedule.every(task_loop_minutes).minutes.do(main, config)
        while True:
            schedule.run_pending()
            time.sleep(1)
