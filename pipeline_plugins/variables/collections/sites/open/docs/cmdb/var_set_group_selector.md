# 集群分组选择器变量
> 版本 `legacy`

## 介绍

全局变量配置，集群分组选择器变量


## 标签

`cmdb` `set_group_selector` 

## 参数说明

### 全局变量设置参数

* `名称`：全局变量名称
* `KEY`: 全局变量名，用于后续引用全局变量
* `描述`: 全局变量描述


### 输入参数

* `set_group_selector`: 集群分组ID 

### 返回参数及格式

* `bk_set_id` 集群ID列表
* `bk_set_name` 集群名称列表
* `flat__set_id` 字符串格式的集群名称
* `flat__set_name` 字符串格式的集群ID
* ...

* 返回格式
```
{
	"bk_alias_name": [],
	"bk_capacity": [],
	"bk_category": [],
	"bk_chn_name": [],
	"bk_customer": [],
	"bk_enable_relate_webplat": [],
	"bk_is_gcs": [],
	"bk_open_time": [],
	"bk_operation_state": [],
	"bk_outer_source": [],
	"bk_platform": [],
	"bk_service_status": ["1"],
	"bk_set_desc": [],
	"bk_set_env": ["3"],
	"bk_set_id": ["8"],
	"bk_set_idc": [],
	"bk_set_name": ["PaaS\u5e73\u53f0"],
	"bk_svc_name": [],
	"bk_system": [],
	"bk_uniq_id": [],
	"bk_world_id": [],
	"description": [],
	"flat__bk_alias_name": "",
	"flat__bk_capacity": "",
	"flat__bk_category": "",
	"flat__bk_chn_name": "",
	"flat__bk_customer": "",
	"flat__bk_enable_relate_webplat": "",
	"flat__bk_is_gcs": "",
	"flat__bk_open_time": "",
	"flat__bk_operation_state": "",
	"flat__bk_outer_source": "",
	"flat__bk_platform": "",
	"flat__bk_service_status": "1",
	"flat__bk_set_desc": "",
	"flat__bk_set_env": "3",
	"flat__bk_set_id": "8",
	"flat__bk_set_idc": "",
	"flat__bk_set_name": "PaaS\u5e73\u53f0",
	"flat__bk_svc_name": "",
	"flat__bk_system": "",
	"flat__bk_uniq_id": "",
	"flat__bk_world_id": "",
	"flat__description": ""
}
```


## 使用说明

> 填写该变量的名称、key以及说明（选填）<br>
> 点击 “默认值” 后面的下拉框，选择一个集群分组


## 样例

![alt](images/var_set_group_selector.png)
