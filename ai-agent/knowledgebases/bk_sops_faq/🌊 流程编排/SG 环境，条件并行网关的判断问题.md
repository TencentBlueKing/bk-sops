问题：
SG 环境，条件并行网关的判断问题，用户的预期是 gromelink 不匹配 gromelink_manager，单配置的是"gromelink" in "(${deployment_type})"，导致判断结果是True

原因：
用户配置的是用户字符串的判断，返回True是正确的

解决方案：
预期是 gromelink 不匹配 gromelink_manager，配置如下：
"gromelink" in ("${deployment_type}")