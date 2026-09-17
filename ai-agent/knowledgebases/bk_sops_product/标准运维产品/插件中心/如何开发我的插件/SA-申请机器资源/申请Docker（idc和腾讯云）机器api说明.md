请求url: http://cfm-portal.bkapps-sz.oa.com/api/sa/apply_docker_machine/

字段说明：


| **字段** | **字段类型** | **是否是可选参数** | **说明（参数值）** |
| - | - | - | - |
| app_id | string | 否 | 业务id |
| reason | string | 否 | 申请原因 |
| follower | string | 否 | 跟进人企业微信（一般填的都是自己） |
| slave_records[].resource_type | string | 否 | 资源类型<br/><br/>IDCDVM（IDC-Docker）  <br/>QCLOUDDVM（腾讯云-Docker） |
| slave_records[].replicas | int | 否 | 申请数量 |
| slave_records[].selector.device_class | string | 否 | 机型 |
| slave_records[].selector.region | string | 否 | 申请机器地域（例如：上海，南京，深圳等） |
| slave_records[].selector.image | string | 否 | 系统镜像（其他镜像请参考SA申请资源中提供的数值）<br/><br/>[hub.oa.com/library/tlinux1.2:v1.17](http://hub.oa.com/library/tlinux1.2:v1.17)<br/><br/>[hub.oa.com/library/tlinux2.2:v1.6](http://hub.oa.com/library/tlinux2.2:v1.6) |
| slave_records[].selector.anti_affinity_level | string | 是（默认值：ANTI_NONE） | 反亲和性策略<br/><br/>ANTI_NONE（无要求）<br/><br/>ANTI_RACK（分机架）<br/><br/>ANTI_MODULE（分模块）<br/><br/>ANTI_CAMPUS（分campus） |
| slave_records[].selector.data_disk_mount_path | string | 是（默认值：/data1） | 挂载盘<br/><br/>/data1<br/><br/>data |
| slave_records[].selector.zone | string | 是（默认值：空字符串（无限制） | 申请机器区域<br/><br/>以申请机器地域-地区的方式（如：上海-宝信） |

参考示例：

```json
{
    "app_id":"706",
    "reason": "测试使用无需过单",
    "follower": "lucifersu",
    "slave_records": [{
        "resource_type": "QCLOUDDVM",
        "replicas": 1,
        "auto_delivery": 1,
        "selector": {
            "anti_affinity_level": "ANTI_NONE",
            "device_class": "D4-8-200-10",
            "image": "hub.oa.com/library/tlinux2.2:v1.6",
            "data_disk_mount_path": "/data1",
            "region": "上海",
            "zone": "上海-宝信"
        }
    }]
}
```

返回示例：

```json
{
    "result": true,
    "code": 0,
    "message": "单据提交成功!",
    "data": {
        "uid": 10073450
    }
}
```