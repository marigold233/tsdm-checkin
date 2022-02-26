# tsdm_checkin
天使动漫签到打工
1. 克隆本仓库
2. 安装依赖
```shell
pip3 install toml requests parsel
```
3. 抓取浏览器网络请求cookie，填入配置文件tsdm_cookie.toml
4. 测试运行脚本`python3.8 tsdm_checkin.py`
![image](https://user-images.githubusercontent.com/62014410/147519880-69da9863-4007-440d-933f-266c8aed64db.png)
6. 加入cron定时任务，完成！  
crontab定时任务示例：
```
*/30 * * * * cd /root/tsdm_checkin/ && /usr/local/bin/python3.8 tsdm_checkin.py &>> checkin.log
```

## TODO
