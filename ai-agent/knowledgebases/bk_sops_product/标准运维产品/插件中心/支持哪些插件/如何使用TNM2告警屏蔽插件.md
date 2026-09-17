1、配置“告警屏蔽”插件

在告警屏蔽插件中，选择输出参数——屏蔽id右边的引用，即可将屏蔽id存入全局变量${shield_id_xxxx}中。

![alt text](image-3.png)

2、配置“告警屏蔽解除”插件

在告警屏蔽解除插件中，输入参数中，配置输入参数的屏蔽策略id，为刚才屏蔽id的全局变量${shield_id_xxxx}即可。

![alt text](image-4.png)