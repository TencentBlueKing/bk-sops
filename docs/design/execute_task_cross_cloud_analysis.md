# execute_task_base.py 跨云区域 IP 执行逻辑分析

## 一、概述

`execute_task_base.py` 中的 `JobExecuteTaskServiceBase` 类在执行作业模板时，对于跨云区域（跨业务）的多个 IP 处理逻辑与同云区域 IP 有显著差异。本文档详细分析这些差异。

## 二、核心方法：build_ip_list

### 2.1 方法签名

```python
def build_ip_list(self, biz_across, val, executor, biz_cc_id, data, ip_is_exist):
```

**参数说明**：
- `biz_across`: 是否允许跨业务（跨云区域）
- `val`: IP 字符串（可能包含多个 IP）
- `executor`: 执行人
- `biz_cc_id`: 业务 ID
- `data`: 节点数据对象
- `ip_is_exist`: 是否校验 IP 存在

### 2.2 执行流程对比

#### 场景 1: 跨业务模式 (`biz_across=True`)

```python
if biz_across:
    # 第一步：尝试跨业务查询
    result, server = self.get_target_server(
        ip_str=val,
        executor=executor,
        biz_cc_id=biz_cc_id,
        data=data,
        is_across=True,          # 关键：启用跨业务查询
        logger_handle=self.logger,
        ip_is_exist=ip_is_exist,
        ignore_ex_data=True,     # 忽略错误数据，不立即返回错误
    )

    # 第二步：如果跨业务查询失败，回退到当前业务查询
    if not result:
        result, server = self.get_target_server(
            ip_str=val,
            executor=executor,
            biz_cc_id=biz_cc_id,
            data=data,
            logger_handle=self.logger,
            is_across=False,     # 回退到当前业务
            ip_is_exist=ip_is_exist,
        )

    if not result:
        return {}
```

**特点**：
1. **双重查询策略**：先跨业务查询，失败后回退到当前业务
2. **容错机制**：`ignore_ex_data=True` 允许第一次查询失败时不立即报错
3. **格式要求**：跨业务查询时，IP 格式必须是 `管控区域ID:IP`（如 `0:127.0.0.1`）

#### 场景 2: 非跨业务模式 (`biz_across=False`)

```python
else:
    result, server = self.get_target_server(
        ip_str=val,
        executor=executor,
        biz_cc_id=biz_cc_id,
        data=data,
        logger_handle=self.logger,
        is_across=False,         # 仅查询当前业务
        ip_is_exist=ip_is_exist,
    )
    if not result:
        return {}
```

**特点**：
1. **单次查询**：仅查询当前业务下的 IP
2. **格式灵活**：可以直接输入 IP，系统会自动从 CMDB 查询对应的管控区域
3. **严格校验**：查询失败立即返回错误

## 三、get_target_server 方法差异

### 3.1 IPv6 场景 (`settings.ENABLE_IPV6=True`)

#### 3.1.1 跨业务查询 (`is_across=True`)

调用 `get_target_server_ipv6_across_business` 方法：

```python
def get_target_server_ipv6_across_business(self, executor, biz_cc_id, ip_str, logger_handle, data):
    """
    跨业务查询流程：
    1. 先在本业务查询 IP，得到两个列表：
       - 本业务查询到的 host
       - 本业务查不到的 IP 列表（包括 IPv4、IPv6、带管控区域的 IP）
    2. 对于本业务查不到的 IP，去全业务查询
    3. 合并查询结果
    """
    # Step 1: 在本业务查询
    (
        host_list,                      # 本业务查询到的 host
        ipv4_not_find_list,            # 本业务查不到的 IPv4
        ipv4_with_cloud_not_find_list, # 本业务查不到的带管控区域的 IPv4
        ipv6_not_find_list,            # 本业务查不到的 IPv6
        ipv6_with_cloud_not_find_list, # 本业务查不到的带管控区域的 IPv6
    ) = cc_get_host_by_innerip_with_ipv6_across_business(executor, biz_cc_id, ip_str, supplier_account)

    # Step 2: 对未找到的 IP，在全业务范围查询
    ip_not_find_str = ",".join(
        ipv4_not_find_list + ipv6_not_find_list +
        ipv4_with_cloud_not_find_list + ipv6_with_cloud_not_find_list
    )

    host_result = cc_get_host_by_innerip_with_ipv6(
        executor, None, ip_not_find_str, supplier_account, is_biz_set=True
    )

    # Step 3: 合并结果
    host_data = host_result["data"] + host_list
    return True, {"host_id_list": [int(host["bk_host_id"]) for host in host_data]}
```

**关键差异**：
- **查询范围**：先本业务，后全业务
- **返回格式**：返回 `host_id_list`（主机 ID 列表）
- **支持格式**：支持 IPv4、IPv6、带管控区域的 IP 混合输入

#### 3.1.2 非跨业务查询 (`is_across=False`)

调用 `get_target_server_ipv6` 方法：

```python
def get_target_server_ipv6(self, executor, biz_cc_id, ip_str, logger_handle, data):
    """
    仅在本业务查询 IP
    """
    host_result = cc_get_host_by_innerip_with_ipv6(executor, biz_cc_id, ip_str, supplier_account)
    if not host_result["result"]:
        return False, {}

    return True, {"host_id_list": [int(host["bk_host_id"]) for host in host_result["data"]]}
```

**关键差异**：
- **查询范围**：仅当前业务
- **返回格式**：返回 `host_id_list`
- **失败处理**：查询失败立即返回错误

### 3.2 IPv4 场景 (`settings.ENABLE_IPV6=False`)

#### 3.2.1 跨业务查询 (`is_across=True`)

调用 `get_biz_ip_from_frontend` 方法，`is_across=True`：

```python
def get_biz_ip_from_frontend(ip_str, executor, biz_cc_id, data, logger_handle, is_across=True, ...):
    """
    跨业务模式下的 IP 处理
    """
    if is_across:
        # 直接解析管控区域:IP 格式，不查询 CMDB
        plat_ip = [match.group() for match in plat_ip_reg.finditer(ip_str)]
        ip_list = [
            {"ip": _ip.split(":")[1], "bk_cloud_id": _ip.split(":")[0]}
            for _ip in plat_ip
        ]
        err_msg = _("允许跨业务时IP格式需满足：【管控区域ID:IP】。失败 IP： {}")
    else:
        # 查询 CMDB 获取 IP 和管控区域信息
        var_ip = cc_get_ips_info_by_str(username=executor, biz_cc_id=biz_cc_id, ip_str=ip_str, use_cache=False)
        ip_list = [
            {"ip": _ip["InnerIP"], "bk_cloud_id": _ip["Source"]}
            for _ip in var_ip["ip_result"]
        ]
        err_msg = _("无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法。查询失败 IP： {}")

    # 校验 IP 格式
    input_ip_set = get_ip_by_regex(ip_str)
    difference_ip_list = list(get_difference_ip_list(input_ip_set, [ip_item["ip"] for ip_item in ip_list]))

    if len(ip_list) != len(set(input_ip_set)):
        return False, ip_list

    return True, ip_list
```

**关键差异**：
- **不查询 CMDB**：直接解析 `管控区域ID:IP` 格式
- **格式要求严格**：必须使用 `管控区域ID:IP` 格式（如 `0:127.0.0.1`）
- **返回格式**：返回 `ip_list`（包含 `ip` 和 `bk_cloud_id`）

#### 3.2.2 非跨业务查询 (`is_across=False`)

调用 `get_biz_ip_from_frontend` 方法，`is_across=False`：

```python
def get_biz_ip_from_frontend(ip_str, executor, biz_cc_id, data, logger_handle, is_across=False, ...):
    """
    非跨业务模式下的 IP 处理
    """
    if is_across:
        # ... 跨业务逻辑
    else:
        # 查询 CMDB 获取 IP 和管控区域信息
        var_ip = cc_get_ips_info_by_str(username=executor, biz_cc_id=biz_cc_id, ip_str=ip_str, use_cache=False)
        ip_list = [
            {"ip": _ip["InnerIP"], "bk_cloud_id": _ip["Source"]}
            for _ip in var_ip["ip_result"]
        ]
        err_msg = _("无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法。查询失败 IP： {}")

    # 校验 IP 格式和存在性
    # ...
```

**关键差异**：
- **查询 CMDB**：通过 CMDB API 查询 IP 的管控区域信息
- **格式灵活**：可以直接输入 IP，系统自动查询管控区域
- **返回格式**：返回 `ip_list`（包含 `ip` 和 `bk_cloud_id`）

## 四、IP 格式要求对比

### 4.1 跨业务模式 (`biz_across=True`)

**IPv4 格式**：
```
0:127.0.0.1,1:192.168.1.1
```
- 格式：`管控区域ID:IP`
- 多个 IP 用逗号或换行分隔
- 必须显式指定管控区域 ID

**IPv6 格式**：
```
0:[2001:db8::1],1:[2001:db8::2]
```
- 格式：`管控区域ID:[IPv6地址]`
- 支持混合输入（IPv4 + IPv6 + 带管控区域的 IP）

### 4.2 非跨业务模式 (`biz_across=False`)

**IPv4 格式**：
```
127.0.0.1,192.168.1.1
```
- 格式：直接输入 IP
- 系统自动从 CMDB 查询管控区域

**IPv6 格式**：
```
[2001:db8::1],[2001:db8::2]
```
- 格式：直接输入 IPv6 地址
- 系统自动从 CMDB 查询管控区域

## 五、执行逻辑差异总结

| 特性 | 跨业务模式 (`biz_across=True`) | 非跨业务模式 (`biz_across=False`) |
|------|-------------------------------|----------------------------------|
| **查询策略** | 双重查询（跨业务 → 当前业务） | 单次查询（仅当前业务） |
| **IP 格式要求** | 必须 `管控区域ID:IP` | 可直接输入 IP |
| **CMDB 查询** | IPv4: 不查询（直接解析）<br>IPv6: 先本业务后全业务 | 查询 CMDB 获取管控区域 |
| **容错机制** | 有（第一次失败可回退） | 无（失败立即返回错误） |
| **返回格式** | IPv4: `ip_list`<br>IPv6: `host_id_list` | IPv4: `ip_list`<br>IPv6: `host_id_list` |
| **错误处理** | `ignore_ex_data=True`（第一次查询） | 立即返回错误 |
| **适用场景** | 跨云区域、跨业务执行 | 同业务内执行 |

## 六、实际执行示例

### 6.1 跨业务场景

**输入**：
```python
biz_across = True
val = "0:127.0.0.1,1:192.168.1.1"
```

**执行流程**：
1. 第一次查询（`is_across=True`）：
   - IPv4 模式：直接解析 `0:127.0.0.1` 和 `1:192.168.1.1`
   - IPv6 模式：先在本业务查询，未找到的在全业务查询

2. 如果第一次查询失败：
   - 回退到当前业务查询（`is_across=False`）
   - 尝试从当前业务 CMDB 查询这些 IP

3. 返回结果：
   ```python
   {
       "ip_list": [
           {"ip": "127.0.0.1", "bk_cloud_id": "0"},
           {"ip": "192.168.1.1", "bk_cloud_id": "1"}
       ]
   }
   ```

### 6.2 非跨业务场景

**输入**：
```python
biz_across = False
val = "127.0.0.1,192.168.1.1"
```

**执行流程**：
1. 查询 CMDB（`is_across=False`）：
   - 调用 `cc_get_ips_info_by_str` 查询当前业务下的 IP
   - 获取每个 IP 对应的管控区域 ID

2. 返回结果：
   ```python
   {
       "ip_list": [
           {"ip": "127.0.0.1", "bk_cloud_id": "0"},  # 从 CMDB 查询得到
           {"ip": "192.168.1.1", "bk_cloud_id": "0"}  # 从 CMDB 查询得到
       ]
   }
   ```

## 七、注意事项

### 7.1 跨业务模式的限制

1. **格式要求严格**：必须使用 `管控区域ID:IP` 格式
2. **白名单要求**：跨业务的 IP 需要在作业平台添加白名单
3. **权限要求**：需要有跨业务权限

### 7.2 错误处理差异

- **跨业务模式**：第一次查询失败不会立即报错，会尝试回退到当前业务查询
- **非跨业务模式**：查询失败立即返回错误，不会尝试其他方式

### 7.3 IPv6 支持

- IPv6 场景下，跨业务查询会先在本业务查询，未找到的再在全业务查询
- 支持 IPv4、IPv6、带管控区域的 IP 混合输入

## 八、代码位置

- **核心方法**：`pipeline_plugins/components/collections/sites/open/job/execute_task/execute_task_base.py`
- **IP 查询逻辑**：`pipeline_plugins/components/collections/sites/open/job/ipv6_base.py`
- **IP 解析工具**：`pipeline_plugins/components/utils/sites/open/utils.py`

## 九、总结

跨云区域多 IP 执行的主要差异在于：

1. **查询策略**：跨业务模式采用双重查询策略，提高容错性
2. **格式要求**：跨业务模式要求显式指定管控区域 ID
3. **CMDB 查询**：跨业务模式（IPv4）不查询 CMDB，直接解析格式
4. **错误处理**：跨业务模式有回退机制，非跨业务模式失败立即返回

这些差异确保了在不同场景下都能正确识别和处理 IP，同时提供了灵活的容错机制。


