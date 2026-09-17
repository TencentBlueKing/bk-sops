## 问题描述：

1. 跑标准运维时遇到了这个问题。 plugin execute raise unexpected error: 获取用户【admin】access_token失败，数据库中不存在记录  
   这个步骤会用到 [https://devops.sg.crosgame.com/](https://devops.sg.crosgame.com/)

## 问题原因：

    1.从devops调用过来的时候传的用户是admin，admin是虚拟的没有access_token

    


## 解决方法：

在标准运维设置执行代理人，希望用谁的身份调用第三方系统的接口 就填谁就行

##   
## 易事厅链接：

[https://zhiyan.woa.com/servicedesk/detail/2723852?proj_id=27&module=14](https://zhiyan.woa.com/servicedesk/detail/2723852?proj_id=27&module=14)

