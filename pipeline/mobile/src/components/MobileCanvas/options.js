/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
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
    isSource: true,
    isTarget: true,
    paintStyle: {},
    hoverPaintStyle: {},
    detachable: false

}
