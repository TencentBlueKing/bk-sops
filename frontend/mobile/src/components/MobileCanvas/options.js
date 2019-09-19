/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
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
export const endpointOptions = {
    endpoint: 'Dot',
    connector: ['Flowchart', { stub: [1, 6], alwaysRespectStub: true, gap: 8, cornerRadius: 2 }], // 'Bezier'、'Straight'、'Flowchart'、'State Machine'，格式 [ type, params]
    connectorOverlays: [
        ['PlainArrow', { width: 8, length: 6, location: 1, id: 'arrow' }]
    ],
    paintStyle: {},
    hoverPaintStyle: {},
    cssClass: 'template-canvas-endpoint',
    isSource: true, // 端点是否可以作为拖动源
    isTarget: true, // 端点是否可以作为拖动目标
    maxConnections: -1
}

/**
 * 节点配置项
 */
export const nodeOptions = {
    grid: [5, 5]
}

/**
 * tips: endpoint 设置 connector 属性后，instance.connect 方法设置 connector 的属性无效
 */
export const connectorOptions = {
    paintStyle: { fill: 'transparent', stroke: '#a9adb6', strokeWidth: 1 },
    hoverPaintStyle: {},
    detachable: false // 是否可以通过鼠标拖动连线
}
