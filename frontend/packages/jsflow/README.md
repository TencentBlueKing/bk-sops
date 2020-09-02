JsFlow 是基于 jsplumb 进行二次封装的 vue 组件。支持左侧拖动源和节点模版的自定义配置，通过传入不同数据源、端点、连线等配置项以及对应的事件选项，可满足各种连线类的应用的需求。

应用实例的 demo 预览，可在代码仓库的根目录下执下命令，并访问 `localhost:8001`

```bash
npm install
npm run dev 
```

## 1.使用方法
---

引用 jsflow 依赖包，在页面注册为组件，即可在页面中使用。
组件的默认框高根据父容器设置。
数据源拖动源、头部工具栏、节点默认使用内置组件，若需要扩展功能和定义样式，可以通过配置 slot 的方式来实现。


> NOTE: **Vue 版本需要在 2.6.0 以上**


更详细的使用方法可参考 demo。

``` html
<js-flow
  :data="data"
  @onConnectionClick="onConnectionClick"
  @onToolClick="onToolClick">
  <template
    v-slot="palettePanel">
    <palette></palette>
  </template>
  <template v-slot="toolPanel">
    <toolPanel></toolPanel>
  </template>
  <template v-slot="nodeTemplate">
    <node-template></node-template>
  </template>
</js-flow>
```

## 2.相关配置
---

### props

`showPalette`: 是否显示拖拽源面板, 类型`Boolean`，默认值显示

`showTool`: 是否显示工具栏（放大、缩小、重置、框选），类型 `Boolean`，默认显示，优先使用通过 slot 定义的工具栏

`selector`: 拖拽源class名称，类型`String`，元素设置该class后，可拖拽，默认为`palette-default-item`

`editable`: 画布是否可编辑，类型`Boolean`，默认为 `true`

`data`: 画布数据，类型`Object`，默认包含两个属性：

  - **`nodes`: 节点数据，类型`Array`，默认为空，单个节点的必需字段如下：**

    - id: 节点id， 类型 `String`
    - x: 节点位于画布水平方向坐标, 类型 `Number`
    - y: 节点位于画布垂直方向坐标, 类型 `Number`
    - type 节点分类，类型 `String`

  - **`lines`: 连线数据，类型`Array`，默认为空，单条连线的必需字段如下：**

    - id: 连线id， 类型 `String`
    - source 连线起始节点信息，类型 `Object`，包括：
      - arrow 连线起点处于起始节点上的哪个位置，类型 `String`，eg: TOP
      - id 起始节点的 id，类型 `String`
    },
    - target
      - arrow 连线终点处于目标节点上的哪个位置，类型 `String`，eg: LEFT
      - id 起始终点的 id，类型 `String`
  
  完整的 data 数据格式例子：
  ```js
    data = {
      nodes: [
        {
          id: 'nodeb662bc1afb5e60daa67e69f48de1',
          x: 20,
          y: 80,
          type: 'startpoint'
        },
        {
          id: 'node74b1ec6275b60d5c22c9848466f1',
          x: 200,
          y: 80,
          type: 'endpoint'
        },
      ],
      lines: [
        {
          id: 'line123feod03j26895c557a452252f0',
          source: {
            arrow: 'Right',
            id: 'nodeb662bc1afb5e60daa67e69f48de1'
          },
          target: {
            arrow: 'Left',
            id: 'node74b1ec6275b60d5c22c9848466f1'
          }
        }
      ]
    }
  ```

`nodeOptions`: 节点配置项，类型 `Object`，支持配置 grid 属性，来设置拖动节点时的最小移动间距，例如： `grid: [5, 5]`

`connectorOptions`: 连线配置项，类型 `Object`，连线的样式与 jsplumb [配置项](http://jsplumb.github.io/jsplumb/paint-styles.html)保持一致，参考配置型如下：
```js
  endpointOptions = {
    endpoint: 'Dot',
    connector: ['Flowchart', { stub: [1, 6], alwaysRespectStub: true, gap: 8, cornerRadius: 2 }], // 'Bezier'、'Straight'、'Flowchart'、'State Machine'，格式 [ type, params]
    connectorOverlays: [
        ['PlainArrow', { width: 8, length: 6, location: 1, id: 'arrow' }]
    ],
    overlays: [
        ['PlainArrow', { location: 1, width: 8, length: 6 }]
    ],
    paintStyle: { fill: 'rgba(0, 0, 0, 0)', stroke: 'rgba(52, 138, 243, 0.15)', strokeWidth: 1, radius: 7 },
    hoverPaintStyle: { fill: '#348af3', stroke: '#348af3' },
    cssClass: 'demo-endpoint',
    hoverClass: 'demo-endpoint-hover',
    maxConnections: -1, // 限制端点最大连线条数，默认值为1，设置为-1表示不限制
    isSource: true, // 端点是否可以作为拖动源
    isTarget: true // 端点是否可以作为拖动目标
}
```

`endpointOptions`: 端点配置项，类型 `Object`，端点的样式与 jsplumb [配置项](http://jsplumb.github.io/jsplumb/paint-styles.html)保持一致，参考配置项如下：
```js
  connectorOptions = {
    paintStyle: { fill: 'transparent', stroke: '#a9adb6', strokeWidth: 2 },
    hoverPaintStyle: { fill: 'transparent', stroke: '#3a84ff' },
    cssClass: 'bk-sops-connector',
    hoverClass: 'bk-sops-connector-hover',
    detachable: true // 是否可以通过鼠标拖动连线
  }
```

`tools`: 工具栏配置项，默认支持放大、缩小、重置、框选，类型 `Array`，支持修改数组元素的顺序，来调整工具项的排列位置，支持通过配置工具项的 `cls` 字段来自定义工具项 class，工具栏位置项默认值为:
  ```js
    [
      {
        type: 'zoomIn',
        name: '放大'
      },
      {
        type: 'zoomOut',
        name: '缩小'
      },
      {
        type: 'resetPosition',
        name: '重置'
      }
    ]
  ```

### 事件

- `onBeforeDrag`: 连线拖动之前，方法返回 true，才会连线，参数 connection
- `onBeforeDrop`: 连线放下之前，方法返回 true，才会连线，参数 connection
- `onConnection`: 连线吸附后，参数 connection
- `onConnectionDrag`: 连线拖动事件回调，参数 connection
- `onBeforeDetach`: 连线删除之前，方法返回 true，才会删除该连线，参数 connection
- `onConnectionDetached`: 连线删除之后，参数 connection，被删除的连线
- `onConnectionMoved`: 连线端点移动到另外端点
- `onConnectionClick`: 连线单击事件回调， 参数 connection, event
- `onConnectionDbClick`: 连线双击事件回调, 参数 connection, event
- `onEndpointClick`: 连线双击事件回调, 参数 endpoint, event
- `onEndpointDbClick`: 连线双击事件回调, 参数 endpoint, event
- `onToolClick`: 工具栏点击元素点击事件回调, 参数 tool
- `onOverlayClick`: overlay 点击事件回调，参数 overlay、event
- `onCreateNodeBefore`: 创建节点之前事件回调，方法返回 true 才会创建, 参数 node
- `onCreateNodeAfter`: 创建节点之前事件回调, 参数 node
- `onNodeMoving`: 节点拖拽移动事件回调, 参数 node, event
- `onNodeMoveStop`: 节点拖拽结束事件回调, 参数 node, event
- `onConnectionDragStop`: 连线拖动到节点上（非端点连接）释放回调, 应用场景之一是连线快速连接，参数 source, targetId, event

### 实例方法

- `createNode`: 创建节点，参数 `node` 配置项(必需)
- `removeNode`: 删除节点，参数 `node` 配置项(必需)
- `createConnector`: 创建连接线, 参数 `line`配置项(必需)、连线是样式相关的配置项(可选)
- `removeConnector`: 删除连接线，参数`line`配置项(必需)
- `getConnectorsByNodeId`: 通过节点id获取所有该节点上所有连接线， 参数`id`配置项
- `addLineOverlay`: 增加连接线overlay，参数`line`配置项(必需)、`overlay`配置项(必需)
- `removeLineOverlay`: 增加连接线overlay，参数`line`配置项(必需)、`id`overlay的id值(必需)
- `zoomIn`: 放大，参数`radio`，默认为 1.1
- `zoomOut`: 缩小，参数`radio`，默认为 0.9
- `resetPosition`: 重置画布位置、缩放比例
- `setCanvasPosition`: 设置画布位置，参数为`x`、`y`，相对于画布左上角为原点
- `setNodePosition`: 更新节点位置，参数`node`配置项(必需)，eg: {id: 'test', x: 200, y: 300}
- `addNodesToDragSelection`: 将节点集合添加到拖拽组中，拖动其中一个节点时，组内节点会一起平移，参数`ids`节点id数组(必需)
- `clearNodesDragSelection`: 取消节点拖拽组


### slots

- `palette`: 节点拖动源，若不传则使用默认组件，默认位置在画布左侧，可自定义可拖动元素的 class，通过 JsFlow 组件的 `selector` props传递到内部。可拖动元素的模版标签上可配置 `data-type`(String)，`data-config`(Object) 分别设置拖动节点的类型和其他配置项：

```html
<ul>
    <li><div class="entry-item" data-type="startpoint">test1</div></li>
    <li><div class="entry-item" data-type="endpoint">test2</div></li>
    <li><div class="entry-item" data-type="tasknode">test3</div></li>
    <li><div class="entry-item" data-type="subflow">test4</div></li>
  </ul>
```
- `nodeTemplate`: 自定义节点模版，若不传则采用默认的节点组件样式。
``` html
<div
  class="bk-flow-location"
  @mousedown="moveFlag = false"
  @mousemove="moveFlag = true"
  @mouseup="onNodeClick(node, $event)">
  <div v-if="node.type === 'startpoint'">startPoint</div>
  <div v-if="node.type === 'endpoint'">endPoint</div>
  <div v-if="node.type === 'tasknode'">taskNode</div>
  <div v-if="node.type === 'subflow'">subFlow</div>
</div>
```
- `toolPanel`: 画布工具栏，若不传则采用默认的工具栏组件。
```html
  <div>
    <div class="tool-item" @click="onCanvasZoomIn">放大</div>
    <div class="tool-item" @click="onCanvasZoomOut">缩小</div>
    <div class="tool-item" @click="onCanvasReset">重置</div>
  </div>
```

## changelog: 
---
  - ### 1.0.1
    - onConnectionDetached 方法的返回值由已存在连线变更为删除的连线
    - 增加更新画布方法 updateCanvas（临时）
    - 去掉框选工具移除，改为使用者用 api 分别调用触发、关闭框选的方式
    - 新增修改连线配置的方法 setConnector
    - 不可编辑态去掉节点 hover 高亮端点
