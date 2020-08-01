### checkmarx rest api 工具，实现自动化项目扫描、报告生成、漏洞数据写入redis

```
## 自动下发扫描，并把扫描项目信息保存在redis create_report key里
python3 main.py -a scan

## 根据redis create_report key里保留的扫描项目信息，对已完成扫描项目生成扫描结果，并保留报告相关信息写入 redis import_redis key中
python3 main.py -a report

## 根据 redis import_redis 保留的信息获取扫描结果并解析，写入redis vulns 中已供消费
python3 main.py -a redis

```