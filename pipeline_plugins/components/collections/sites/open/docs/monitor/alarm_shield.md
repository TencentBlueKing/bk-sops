# 监控平台(Monitor) - 蓝鲸监控告警屏蔽(按范围)

### 介绍

蓝鲸监控告警屏蔽(按范围)

### 标签

`Monitor` `alarm_shield`

### 参数说明

#### 输入参数说明

- 屏蔽范围: 告警屏蔽范围（业务、IP、结点）
    
    - 业务
    - IP 多个用逗号分隔
    - 结点
        - 大区获取方式(从CMDB获取、手动输入)
        - 集群 集群名，多个用英文逗号 `,` 分隔开
        - 服务模板获取方式(从CMDB获取、手动输入)
        - 模块 模块名，多个用英文逗号 `,` 分隔开

- 指标： 屏蔽指标

- 开始时间： 时间格式 yyyy-MM-dd HH:mm:ss，建议引用自定义时间日期变量

- 结束时间：时间格式 yyyy-MM-dd HH:mm:ss，建议引用自定义时间日期变量

#### 输出参数说明

- 屏蔽Id

- 详情

### 样例

- 屏蔽范围选择业务示例

![](image/monitor_alarm_shield_biz.png)

- 屏蔽范围选择IP示例

![](image/monitor_alarm_shield_ip.png)

- 屏蔽范围选择结点示例

    - 从CMDB拉取
    
        ![](image/monitor_alarm_shield_node_select.png)
        
    - 手动输入
    
        ![](image/monitor_alarm_shield_node_input.png)

### 注意事项
