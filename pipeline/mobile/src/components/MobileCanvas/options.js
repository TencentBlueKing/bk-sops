// 连接线配置项
export const connectorOptions = {
    paintStyle: {
        strokeWidth: 1,
        stroke: '#666',
        outlineWidth: 1
    },
    overlays: [['PlainArrow', { width: 8, length: 6, location: 1 }]],
    connector: ['Flowchart']
}

export const endpointOptions = {
    endpoint: 'Rectangle',
    anchor: ['Top', 'Right', 'Bottom', 'Left'],
    isSource: false,
    isTarget: true,
    paintStyle: {},
    hoverPaintStyle: {},
    detachable: false

}
