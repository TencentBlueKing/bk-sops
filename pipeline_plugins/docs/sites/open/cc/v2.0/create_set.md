# 创建集群

## 介绍

在用户选择的父实例下创建集群

## 标签
`cc` `cmdb` `create_set` 

## 参数说明

* `biz_cc_id` 业务id

* `cc_select_set_parent_method` 选择父实例的方式
    * `text`: 文本输入
    * `topo`: 树形组件上勾选

* `cc_set_parent_select_topo` 树形组件勾选的父实例列表
   * 列表元素结构：`{bz_inst_name}_{bz_inst_id}`

* `cc_set_parent_select_text` 文本输入的父实例路径集合
    * 换行区分路径，`>`区分层级
    * example: `a>b>c\n   a>b`
    * 已容错：冗余回车/空格
 
 * `cc_st_info` 集群信息
    * `bk_set_name` 集群名称
    * `bk_set_desc` 集群描述
    * `bk_set_env` 环境类型
    * `bk_service_status` 服务状态
    * `description` 备注
    * `bk_capacity` 集群容量

## 输出参数说明

* 执行结果：

  系统展示的插件执行结果

## 样例

![](images/create_set_topo.png)

切换为手动输入

![](images/create_set_text.png)

## 注意事项

* `cc_set_parent_select_topo` 字段只在`cc_select_set_parent_method`为`topo`时有效

* `cc_set_parent_select_text` 字段只在`cc_select_set_parent_method`为`text`时有效
  

  