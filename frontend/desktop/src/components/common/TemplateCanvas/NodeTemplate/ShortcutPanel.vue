/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div
        ref="shortcutWrap"
        v-if="idOfNodeShortcutPanel === node.id"
        :style="{ top: shortcutPanelTop }"
        class="shortcut-panel"
        @mouseover.stop>
        <ul class="shortcut-wrap">
            <li
                v-if="isShowConfigIcon"
                class="shortcut-item common-icon-gear"
                @click.stop="onConfigBtnClick"></li>
            <li
                v-if="isShowConfigIcon"
                class="shortcut-item common-icon-double-paper-2"
                @click.stop="onCopyBtnClick"></li>
            <li
                v-for="(name, index) in nodeTypeList"
                :key="index"
                :class="['shortcut-item', `common-icon-node-${name}-shortcut`]"
                @click.stop="onAppendNode(name)"></li>
        </ul>
    </div>
</template>
<script>
    import { uuid } from '@/utils/uuid.js'
    import tools from '@/utils/tools.js'
    export default {
        name: 'ShortcutPanel',
        props: {
            canvasData: {
                type: Object,
                default () {
                    return {}
                }
            },
            node: {
                type: Object,
                default () {
                    return {}
                }
            },
            editable: {
                type: Boolean,
                default: true
            },
            idOfNodeShortcutPanel: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                nodeTypeList: ['tasknode', 'subflow', 'parallelgateway', 'branchgateway', 'convergegateway']
            }
        },
        computed: {
            currentLocation () {
                return this.canvasData.locations.find(m => m.id === this.idOfNodeShortcutPanel) || {}
            },
            // 是否显示节点配置 icon
            isShowConfigIcon () {
                return ['tasknode', 'subflow'].indexOf(this.currentLocation.type) !== -1
            },
            shortcutPanelTop () {
                if (this.isGatewayNode(this.node.type)) {
                    return '46px'
                }
                if (this.node.type === 'startpoint') {
                    return '52px'
                }
                return '64px'
            }
        },
        methods: {
            onConfigBtnClick () {
                this.$emit('onConfigBtnClick', this.idOfNodeShortcutPanel)
            },
            /**
             * 添加节点
             * @param {String} type -添加节点类型
             */
            onAppendNode (type, isFillParam = false) {
                const { x, y, id, type: currType } = this.currentLocation
                const endX = x + 200
                const newNodeId = 'node' + uuid()
                let location = {}
                if (isFillParam) {
                    location = tools.deepClone(this.node)
                    location.oldSouceId = id
                    location.id = newNodeId
                    location.x = endX
                } else {
                    location = {
                        type,
                        y,
                        x: endX,
                        mode: 'edit',
                        id: newNodeId
                    }
                }
                const line = {
                    source: {
                        arrow: 'Right',
                        id: id
                    },
                    target: {
                        id: newNodeId,
                        arrow: 'Left'
                    }
                }
                // 后面是否已存在节点
                let endNodeId = ''
                const isHaveNodeBehind = this.canvasData.lines.some(line => {
                    if (line.source.id === id) {
                        endNodeId = line.target.id
                        return true
                    }
                })
                const isGatewayCurrNode = this.isGatewayNode(currType)
                const isGatewayAppendNode = this.isGatewayNode(type)
                if (currType === 'startpoint') {
                    location.y += isGatewayAppendNode ? 5 : -5
                } else {
                    if (isGatewayCurrNode && !isGatewayAppendNode) {
                        location.y -= 10
                    }
                    if (!isGatewayCurrNode && isGatewayAppendNode) {
                        location.y += 10
                    }
                }
                
                /**
                 * 添加规则
                 * 当前节点类型为并行/分支网管：都是 onAppendNode
                 * 其他节点类型：后面有节点为插入，没有为追加
                 */
                if (isHaveNodeBehind && ['tasknode', 'subflow', 'convergegateway', 'startpoint'].indexOf(currType) > -1) {
                    this.$emit('onInsertNode', {
                        startNodeId: id,
                        endNodeId,
                        location,
                        isFillParam
                    })
                } else {
                    if (['parallelgateway', 'branchgateway'].indexOf(currType) > -1 && isHaveNodeBehind) {
                        // 拿到并行中最靠下的节点
                        const { x: parallelX, y: parallelY } = this.getParallelNodeMinDistance(id)
                        location.y = parallelY + 100
                        location.x = parallelX
                    }
                    this.$emit('onAppendNode', { location, line, isFillParam })
                }
            },
            // 是不是网关节点
            isGatewayNode (type) {
                return ['parallelgateway', 'branchgateway', 'convergegateway'].indexOf(type) > -1
            },
            // 是否存在节点在需要追加节点后面
            isHaveNodeBehind (id) {
                return this.canvasData.lines.some(line => line.source.id === id)
            },
            /**
             * 获得并行节点中最靠下面的节点
             * @param {String} nodeId 并行网管/分支网管
             */
            getParallelNodeMinDistance (nodeId) {
                const { lines, locations } = this.canvasData
                const { y } = locations.find(m => m.id === nodeId)
                const parallelNodes = lines.filter(m => m.source.id === nodeId).map(m => m.target.id)
                let maxDistance = null
                // 距离网管节点垂直距离最近的节点
                let needNodeLocation = null
                locations.forEach((m, index) => {
                    if (parallelNodes.indexOf(m.id) > -1) {
                        if (maxDistance === null) {
                            maxDistance = m.y - y
                            needNodeLocation = m
                        } else if (parallelNodes.indexOf(m.id) && m.y - y > maxDistance) {
                            maxDistance = m.y - y
                            needNodeLocation = m
                        }
                    }
                })
                return needNodeLocation
            },
            // 克隆当前节点
            onCopyBtnClick () {
                this.onAppendNode(this.node.type, true)
            }
        }
    }
</script>
<style lang="scss">
.shortcut-panel {
    position: absolute;
    left: 50%;
    top: 56px;
    width: 120px;
    transform: translateX(-50%);
    cursor: default;
    .shortcut-wrap {
        display: flex;
        align-items: center;
        justify-content: left;
        flex-wrap: wrap;
        padding: 9px 12px 0px 14px;
        width: 120px;
        overflow: hidden;
        border-radius: 4px;
        background: rgba(255, 255, 255, .9);
        .shortcut-item {
            margin-bottom: 11px;
            width: 24px;
            height: 24px;
            line-height: 24px;
            text-align: center;
            font-size: 24px;
            color: #52699d;
            cursor: pointer;
            &:not(:nth-child(3n)) {
                margin-right: 11px;
            }
            &:hover {
                color: #3a84ff;
            }
        }
    }
}
</style>
