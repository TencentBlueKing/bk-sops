/**
 * connector 类型
 * 1. Bezier 贝塞尔曲线，默认使用
 * 配置项：
 * curviness 曲率
 * 2. Straight 直线
 * 配置项：
 * stub 默认为 0
 * gap 连线到端点的间距, 默认为 0
 * 3.Flowchart 流程图
 * 配置项：
 * stub
 * alwaysRespectStubs
 * gap 连线到端点的间距
 * midpoint 连线分段的比例，默认为 0.5
 * cornerRadius 连线分段点的弧度，默认为 0
 */
const options = {
    // 端点配置项
    // endpoint 设置 connector 属性后，instance.connect 方法设置 connector 的属性无效
    endpointOptions: {
        endpoint: 'Dot',
        connector: ['Flowchart', { stub: [1, 6], alwaysRespectStub: true, gap: 8, cornerRadius: 2 }], // 'Bezier'、'Straight'、'Flowchart'、'State Machine'，格式 [ type, params]
        connectorOverlays: [
            ['PlainArrow', { width: 8, length: 6, location: 1, id: 'arrow' }]
        ],
        paintStyle: { fill: 'rgba(0, 0, 0, 0)', stroke: 'rgba(52, 138, 243, 0.15)', strokeWidth: 1, radius: 7 },
        hoverPaintStyle: { fill: '#348af3', stroke: '#348af3' },
        cssClass: 'template-canvas-endpoint',
        hoverClass: 'template-canvas-endpoint-hover',
        isSource: true, // 端点是否可以作为拖动源
        isTarget: true // 端点是否可以作为拖动目标
    },
    // 节点配置项
    nodeOptions: {
        grid: [5, 5]
    },
    // 连线配置项
    connectorOptions: {
        paintStyle: { fill: 'transparent', stroke: '#a9adb6', strokeWidth: 2 },
        hoverPaintStyle: { fill: 'transparent', stroke: '#3a84ff' },
        cssClass: 'bk-sops-connector',
        hoverClass: 'bk-sops-connector-hover',
        detachable: true // 是否可以通过鼠标拖动连线
    }
}

export default options
