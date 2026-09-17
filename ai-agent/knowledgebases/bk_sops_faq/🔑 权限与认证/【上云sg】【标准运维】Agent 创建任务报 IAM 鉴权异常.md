## 问题描述：

通过 Agent 调用标准运维创建任务接口时报错，

接口返回 code 3599999，message 为 iam authentication exception，失败动作是 flow_create_task。虽然 HTTP 状态码是 200，但业务实际执行失败，本质是当前调用账号没有创建任务所需的 IAM 权限。


## 解决方法：

检查当前请求实际使用的账号身份（如 bk_username 对应账号），并在 IAM 中为该账号申请 flow_create_task 权限；


如果不希望使用 Agent 账号执行，可将 bk_username 改为调用人自己的账号，并确保该账号已有相同权限；


如果是固定流程长期运行，也可以配置流程执行代理人，由具备权限的代理账号执行。建议优先使用调用人自己的权限，避免共用 Agent 权限带来的风险。

