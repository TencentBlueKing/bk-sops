## 问题描述：

1. 任务执行开始节点报错context hydrate failed(list index out of range), check node log for details

## 问题原因：

    1.IP选择器配成常量了，那么就会在开始节点去渲染 ip，但是渲染的时候没有正确的配置，所以在开始节点渲染失败

    


## 解决方法：

IP选择器设置一个默认配置

##   

