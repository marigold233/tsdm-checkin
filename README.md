# tsdm-checkin
天使动漫签到打工
1. 克隆本仓库
```shell
git clone https://github.com/marigold233/tsdm_checkin.git
```
2. 安装依赖
```shell
pip3 install -r requirements.txt
```
3. 抓取浏览器网络请求cookie，填入配置文件config.toml
![image](https://user-images.githubusercontent.com/62014410/155866120-d9dc424c-6472-45f5-b1e4-61d35ba4cd18.png)
4. 测试运行脚本
```shell
python3.8 tsdm_checkin.py
```
![image](https://user-images.githubusercontent.com/62014410/147519880-69da9863-4007-440d-933f-266c8aed64db.png)
5. 加入cron定时任务，crontab定时任务示例：
```
*/30 * * * * cd /root/tsdm_checkin/ && /usr/local/bin/python3.8 tsdm_checkin.py &>> checkin.log
```

## TODO
1. 增加活动祝福语回复（可以获得天使币和威望）
2. 日志输出优化
3. 支持钉钉推送签到打工结果
