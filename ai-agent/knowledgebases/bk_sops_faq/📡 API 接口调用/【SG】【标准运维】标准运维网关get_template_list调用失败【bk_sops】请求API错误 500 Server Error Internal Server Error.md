## 问题描述：
sg 环境标准运维网关get_template_list调用失败
【bk_sops】请求API错误：500 Server Error: Internal Server Error for url: https://bkapi.sg.crosgame.com/api/bk-sops/prod/get_template_list/xxx/?bk_biz_id=xxxx

```html
<!doctype html>
<html lang="en">
<head>
  <title>Server Error (500)</title>
</head>
<body>
  <h1>Server Error (500)</h1><p></p>
</body>
</html>
```

## 问题原因：
用户使用的是虚拟用户，需要开发将虚拟用户手动加到标准运维，不然没这个虚拟用户。
    
 
## 解决方法：
需要将虚拟用户手动加到标准运维

## 易事厅链接：
https://zhiyan.woa.com/servicedesk/detail/2725397?proj_id=27