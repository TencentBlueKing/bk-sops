## 版本日志接入文档

#### 安装
- Cli:

```shell
npm install -g @blueking/log-version
```
- In-browser:

```shell
npm install @blueking/log-version
```

#### 使用

```vue
  <script>
    improt logVersion from '@blueking/log-version'
    export default {
      ...
      components {
        logVersion
      }
      ...
    }
  </script>

  <template>
    <log-version
        ref="versionLog"
        :log-list="logList"
        :log-detail="logDetail"
        :loading="logListLoading || logDetailLoading"
        @active-change="handleVersionChange">
    </log-version>
  </template>
```
#### 属性

| 参数 | 说明 | 类型 | 可选值| 默认值 |
| --- | --- | -- | -- | -- |
|  loading   |  log右侧内容加载loading   | Boolean   |  true, false  | false |
|  logList   |  log左侧列表   | Array   |  []  |  [] |
|  logDetail   |  日志内容   | String   |  ''  | ''  |
|  markdown   |  支持mark语法   | Boolean   |  true, false  | true |
|  dialogProps   |  日志组件内dialog的props   | Object   |  --  | {} |

#### 事件

| 参数 | 说明 | 类型 | 返回值|
| --- | --- | -- | -- |
|   active-change  |  切换版本日志时触发   |  Object  |  currentRow  |