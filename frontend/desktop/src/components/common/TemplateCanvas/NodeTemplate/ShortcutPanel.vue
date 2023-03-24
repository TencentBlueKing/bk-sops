/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
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
        :style="{ left: `${position.left}px`, top: `${position.top}px` }"
        class="shortcut-panel"
        @mouseover.stop
        @click.stop>
        <ul class="nodes-wrap">
            <li
                v-for="(item, index) in nodeTypeList"
                :key="index"
                v-bk-tooltips="{
                    content: item.tips,
                    delay: 500
                }"
                :data-test-id="`templateCanvas_panel_${item.key}`"
                :class="['nodes-item', `common-icon-node-${item.key}-shortcut`]"
                @click.stop="onAppendNode(item.key)">
            </li>
        </ul>
        <ul class="operate-btns" v-if="nodeOperate || deleteLine">
            <template v-if="nodeOperate">
                <li
                    v-bk-tooltips="{
                        content: $t('复制节点'),
                        delay: 500
                    }"
                    data-test-id="templateCanvas_panel_nodeCopy"
                    class="btn-item common-icon-bkflow-copy"
                    @click.stop="onAppendNode(node.type, true)">
                </li>
                <li
                    v-bk-tooltips="{
                        content: $t('复制并插入'),
                        delay: 500
                    }"
                    data-test-id="templateCanvas_panel_nodeCopyInsert"
                    class="btn-item common-icon-bkflow-copy-insert"
                    @click.stop="onAppendNode(node.type, true, true)">
                </li>
                <li
                    v-if="isHasLines"
                    v-bk-tooltips="{
                        content: $t('解除连线'),
                        delay: 500
                    }"
                    data-test-id="templateCanvas_panel_nodeDisconnect"
                    class="btn-item common-icon-bkflow-disconnect"
                    @click.stop="$emit('onNodeRemove', node, false)">
                </li>
                <li
                    v-bk-tooltips="{
                        content: $t('删除节点'),
                        delay: 500
                    }"
                    data-test-id="templateCanvas_panel_nodeDelete"
                    class="btn-item common-icon-bkflow-delete"
                    @click.stop="$emit('onNodeRemove', node)">
                </li>
            </template>
            <li
                v-if="deleteLine"
                v-bk-tooltips="{
                    content: $t('删除连线'),
                    delay: 500
                }"
                data-test-id="templateCanvas_panel_lineDelete"
                class="btn-item common-icon-bkflow-delete"
                @click.stop="$emit('onDeleteLineClick')">
            </li>
        </ul>
    </div>
</template>
<script>
    import { uuid } from '@/utils/uuid.js'
    import tools from '@/utils/tools.js'
    import i18n from '@/config/i18n/index.js'
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
            line: {
                type: Object,
                default () {
                    return {}
                }
            },
            editable: {
                type: Boolean,
                default: true
            },
            nodeOperate: {
                type: Boolean,
                default: false
            },
            deleteLine: {
                type: Boolean,
                default: false
            },
            position: {
                type: Object,
                default () {
                    return {
                        left: 0,
                        top: 0
                    }
                }
            }
        },
        data () {
            return {
                nodeTypeList: [
                    { key: 'tasknode', tips: i18n.t('标准插件节点') },
                    { key: 'subflow', tips: i18n.t('子流程节点') },
                    { key: 'parallelgateway', tips: i18n.t('并行网关') },
                    { key: 'branchgateway', tips: i18n.t('分支网关') },
                    { key: 'convergegateway', tips: i18n.t('汇聚网关') },
                    { key: 'conditionalparallelgateway', tips: i18n.t('条件并行网关') }
                ]
            }
        },
        computed: {
            isHasLines () {
                const lines = this.canvasData.lines.filter(line => [line.source.id, line.target.id].includes(this.node.id))
                return !!lines.length
            }
        },
        methods: {
            onConfigBtnClick () {
                this.$emit('onConfigBtnClick', this.node.id)
            },
            /**
             * 添加节点
             * @param {String} type -添加节点类型
             */
            onAppendNode (type, isFillParam = false, insert = false) {
                const { x, y, id, type: currType } = this.node
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
                const isHaveNodeBehind = this.canvasData.lines.some(line => line.source.id === id)
                const isGatewayCurrNode = this.isGatewayNode(currType)
                const isGatewayAppendNode = this.isGatewayNode(type)
                if (currType === 'startpoint') {
                    location.y += isGatewayAppendNode ? 0 : -10
                } else {
                    if (isGatewayCurrNode && !isGatewayAppendNode) {
                        location.y -= 10
                    }
                    if (!isGatewayCurrNode && isGatewayAppendNode) {
                        location.y += 10
                    }
                }

                // 复制节点并且不插入
                if (isFillParam && !insert) {
                    this.$emit('onCopyNode', location)
                    return
                }
                /**
                 * 添加规则
                 * 当前节点类型为并行/分支网管：都是 onAppendNode
                 * 其他节点类型：后面有节点为插入，没有为追加
                 */
                if ((isHaveNodeBehind && ['tasknode', 'subflow', 'convergegateway', 'startpoint'].indexOf(currType) > -1) || this.line) {
                    let endNodeId = ''
                    if (this.line) {
                        endNodeId = this.line.targetId
                    } else {
                        const fstNodeLine = this.canvasData.lines.find(line => line.source.id === id)
                        endNodeId = fstNodeLine.target.id
                    }
                    if (['parallelgateway', 'branchgateway', 'conditionalparallelgateway'].indexOf(currType) > -1 && isHaveNodeBehind) {
                        const conditions = this.canvasData.branchConditions
                        if (conditions[id] && Object.keys(conditions[id]).length > 1) {
                            // 拿到并行中最靠下的节点
                            const { x: parallelX, y: parallelY } = this.getParallelNodeMinDistance(id)
                            location.y = parallelY + 100
                            location.x = parallelX
                        }
                    }
                    this.$emit('onInsertNode', {
                        startNodeId: id,
                        endNodeId,
                        location,
                        isFillParam
                    })
                } else {
                    if (['parallelgateway', 'branchgateway', 'conditionalparallelgateway'].indexOf(currType) > -1 && isHaveNodeBehind) {
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
                return ['parallelgateway', 'branchgateway', 'convergegateway', 'conditionalparallelgateway'].indexOf(type) > -1
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
                const { x, y } = locations.find(m => m.id === nodeId)
                const parallelNodes = lines.filter(m => m.source.id === nodeId).map(m => m.target.id)
                let maxDistance = null
                // 距离网管节点垂直距离最近的节点
                let needNodeLocation = { x: x + 200, y } // 默认新增节点坐标
                locations.forEach((m, index) => {
                    if (m.type === 'tasknode' && parallelNodes.indexOf(m.id) > -1) {
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
            }
        }
    }
</script>
<style lang="scss">
.shortcut-panel {
    position: absolute;
    width: 128px;
    background: rgba(255, 255, 255, .9);
    cursor: default;
    z-index: 6;
    .nodes-wrap {
        display: flex;
        align-items: center;
        justify-content: left;
        flex-wrap: wrap;
        padding: 9px 12px 0px;
        width: 128px;
        overflow: hidden;
        border-radius: 4px;
        .nodes-item {
            margin-bottom: 10px;
            width: 24px;
            height: 24px;
            line-height: 24px;
            text-align: center;
            font-size: 24px;
            color: #52699d;
            cursor: pointer;
            &:not(:nth-child(3n)) {
                margin-right: 16px;
            }
            &:hover {
                color: #3a84ff;
            }
            &.common-icon-node-tasknode-shortcut,
            &.common-icon-node-subflow-shortcut {
                font-size: 18px;
            }
        }
    }
    .operate-btns {
        padding: 6px 12px;
        text-align: left;
        background: #f5f7fa;
        .btn-item {
            display: inline-block;
            margin-left: 8px;
            color: #52699d;
            font-size: 16px;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
            &:first-child {
                margin-left: 0;
            }
        }
    }
}
</style>
