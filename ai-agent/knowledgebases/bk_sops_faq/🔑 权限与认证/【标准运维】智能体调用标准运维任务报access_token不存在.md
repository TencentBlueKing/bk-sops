## 问题描述：

智能体调用标准运维任务时执行失败，报错：获取用户access_token失败，数据库中不存在记录。
![alt text](image-10.png)

## 解决方法：

智能体需要先在网页端访问一次，触发 access_token 生成，之后才能正常调用。

参考文档：https://iwiki.woa.com/p/4009265804