## 问题：
bk-plugin-framework   因为这个版本太低apigw不能同步，导致各种各样的问题
```
("data":null,"message":"Parameters error [reason="user authentication failed, please provide a valid user identity,
such as bk username, bk token, access token "1,"result":false,"code":1640001,"code name"."INVALID ARGS")
```
## 原因
bk-plugin-framework 由于版本迭代，在2.0.0版本后读取的是BKPAAS_DEFAULT_PREALLOCATED_URLS这个环境变量，而sg环境已经没有BKPAAS_ENGINE_APP_DEFAULT_SUBDOMAINS 环境变量了。

解决：
升级bk-plugin-framework版本到2.0.0以上