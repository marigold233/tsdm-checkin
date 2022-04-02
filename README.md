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

3. 抓取浏览器网络请求cookie，填入配置文件config.toml，并配置相关推送信息
![image](https://user-images.githubusercontent.com/62014410/155866120-d9dc424c-6472-45f5-b1e4-61d35ba4cd18.png)

4. 测试运行脚本，然后 `ctrl + C` 退出  
```shell
python3 tsdm_checkin.py
```
![image](https://user-images.githubusercontent.com/62014410/161245123-694a72ef-2c1f-449e-b8eb-06b39525a03b.png)

5. 放入后台启动：
```shell
nohup python3 tsdm_checkin.py &
```

6. 查看进程是否存在
```shell
ps -ef | grep "tsdm_checkin"
```

## 其它
```shell
# 杀掉进程
pgrep -f tsdm_checkin.py | xargs kill

# checkin.log --> 签到打工日志
```

## TODO
1. 增加活动祝福语回复（可以获得天使币和威望）  
2. ~~日志输出优化~~  
3. ~~支持钉钉推送签到打工结果~~  
4. ~~使用定时任务相关库，不依赖于linux cron~~    
