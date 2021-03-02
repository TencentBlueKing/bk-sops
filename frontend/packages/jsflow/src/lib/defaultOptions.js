// 节点配置项
export const nodeOptions = {
    grid: [5, 5]
}

// 节点添加栏配置项
export const paletteOptions = {
    selector: 'palette-default-item',
    quickConnect: true
}

// 连接线配置项
export const connectorOptions = {
    connector: ['Bezier', { curviness: 30 }],
    paintStyle: {
        strokeWidth: 2,
        stroke: '#567567',
        outlineStroke: 'tranparent',
        outlineWidth: 6
    },
    hoverPaintStyle: { fill: 'transparent', stroke: '#3a84ff' }
}

// 端点配置项
export const endpointOptions = {
    endpoint: 'Dot',
    connector: ['Flowchart', { stub: [1, 6], alwaysRespectStub: true, gap: 8, cornerRadius: 2 }],
    connectorOverlays: [
        ['PlainArrow', { width: 8, length: 6, location: 1, id: 'arrow' }]
    ],
    paintStyle: { fill: '#3a84ff', radius: 5 },
    anchor: ['Left', 'Right', 'Top', 'Bottom'],
    isSource: true,
    isTarget: true
}
