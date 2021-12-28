#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import requests
import toml
from parsel import Selector
from urllib.parse import urljoin


BASE_URL = 'https://www.tsdm39.net'
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def read_cookie(cookie_file):
    user_cookies = toml.load(cookie_file)
    if not user_cookies.get('cookies'):
        logger.error('未找到用户cookie')
        return
    return user_cookies.get('cookies')


def tsdm_login(cookie):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.36 Safari/537.36 Edg/97.0.1072.28",
        "Cookie": cookie
    }
    login_url = urljoin(BASE_URL, 'forum.php')
    session = requests.Session()
    session.headers = headers
    login_response = session.get(login_url)
    selector = Selector(text=login_response.text)
    if selector.css('#ls_username') and selector.css('#ls_password'):
        logger.error('cookie已经失效，请重新登录获取cookie')
        return
    return session


def tsdm_work(session):
    work_url = urljoin(BASE_URL, 'plugin.php?id=np_cliworkdz:work')
    response = session.get(work_url)
    tips = Selector(text=response.text).xpath(
        '//*[@id="messagetext"]/p[1]/text()')
    if tips:
        logger.info('打工%s' % ''.join(tips.getall()))
        return
    for n in range(6):
        session.post(work_url, data={"act": "clickad"})
        logger.info("正在点击第%s广告" % n)
    response = session.post(work_url, data={"act": "getcre"})
    message = '打工完成，%s' % ''.join(Selector(text=response.text)
                                  .css('#messagetext.alert_info p')
                                  .re('<p>(.*?)<br>(.*?)<script'))
    logger.info(message)


def checkin(session):
    checkin_url = urljoin(BASE_URL, 'plugin.php?id=dsu_paulsign:sign')
    response = session.get(checkin_url)
    from_hash = Selector(text=response.text).xpath(
        '//*[@id="qiandao"]/input/@value').get()
    if not from_hash:
        # logger.info("签到： 今天已经签到过了")
        return True
    checkin_api = urljoin(
        BASE_URL, 'plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=1')
    data = {
        "formhash": from_hash,
        "qdxq": "ch",
        "qdmode": 3,
        "fastreply": 0
    }
    checkin_response = session.post(checkin_api, data=data)
    logger.info("TSDM签到成功")
    

if __name__ == '__main__':
    cookies = read_cookie('tsdm_cookie.toml')
    for user, cookie in cookies.items():
        session = tsdm_login(cookie)
        if session:
            checkin(session)
            tsdm_work(session)
