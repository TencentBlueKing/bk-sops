/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="palette-panel">
        <div class="palette-container">
            <div
                :class="[
                    'palette-item',
                    'entry-item',
                    { disabled: isDisableStartPoint }
                ]"
                data-config-name=""
                data-type="startpoint">
                <div class="node-type-text start-point">{{ i18n.start }}</div>
            </div>
            <div
                :class="[
                    'palette-item',
                    'entry-item',
                    { disabled: isDisableEndPoint }
                ]"
                data-config-name=""
                data-type="endpoint">
                <div class="node-type-text end-point">{{ i18n.end }}</div>
            </div>
            <div
                :class="['palette-item', 'entry-item', 'palette-with-menu', { actived: activeNodeListType === 'tasknode' }]"
                data-type="tasknode"
                @mousedown="onNodeMouseDown('tasknode', $event)"
                @click="onOpenNodeMenu('tasknode', $event)">
                <div class="node-type-icon common-icon-node-tasknode"></div>
            </div>
            <div
                :class="['palette-item','entry-item', 'palette-with-menu', { actived: activeNodeListType === 'subflow' }]"
                data-type="subflow"
                @mousedown="onNodeMouseDown('subflow', $event)">
                <div class="node-type-icon common-icon-node-subflow"></div>
            </div>
            <div class="palette-item entry-item" data-config-name="" data-type="parallelgateway">
                <div class="node-type-icon common-icon-node-parallelgateway"></div>
            </div>
            <div class="palette-item entry-item" data-config-name="" data-type="branchgateway">
                <div class="node-type-icon common-icon-node-branchgateway"></div>
            </div>
            <div class="palette-item entry-item" data-config-name="" data-type="convergegateway">
                <div class="node-type-icon common-icon-node-convergegateway"></div>
            </div>
        </div>
        <node-menu
            :show-node-menu="showNodeMenu"
            :is-fixed-node-menu="isFixedNodeMenu"
            :active-node-list-type="activeNodeListType"
            :nodes="nodes"
            @onCloseNodeMenu="onCloseNodeMenu"
            @onToggleNodeMenuFixed="onToggleNodeMenuFixed">
        </node-menu>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import NodeMenu from './NodeMenu.vue'

    export default {
        name: 'PalattePanel',
        components: {
            NodeMenu
        },
        props: {
            atomTypeList: {
                type: Object,
                default () {
                    return {}
                }
            },
            isDisableStartPoint: {
                type: Boolean,
                default: false
            },
            isDisableEndPoint: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                activeNodeListType: '',
                showNodeMenu: false,
                isFixedNodeMenu: false,
                nodeMouse: {
                    type: '',
                    startX: null,
                    startY: null
                },
                moveFlag: {
                    x: 0,
                    y: 0
                },
                i18n: {
                    start: gettext('开始'),
                    end: gettext('结束')
                }
            }
        },
        computed: {
            nodes () {
                const data = this.atomTypeList[this.activeNodeListType]
                return data || []
            }
        },
        watch: {
            showNodeMenu (val) {
                this.$emit('updateNodeMenuState', val)
            }
        },
        mounted () {
            this.$emit('registerPaletteEvent')
        },
        methods: {
            onMouseDown (e) {
                this.moveFlag = {
                    x: e.pageX,
                    y: e.pageY
                }
            },
            onOpenNodeMenu () {
                this.showNodeMenu = true
                this.activeNodeListType = this.nodeMouse.type
            },
            onCloseNodeMenu () {
                this.showNodeMenu = false
                this.activeNodeListType = ''
            },
            onToggleNodeMenuFixed (val) {
                this.isFixedNodeMenu = val
            },
            /**
             * 节点点击，区分是 展开菜单 还是 拖拽
             * @param {String} type -node type
             * @param {Object} e -event
             */
            onNodeMouseDown (type, e) {
                this.nodeMouse.startX = e.pageX
                this.nodeMouse.startY = e.pageY
                this.nodeMouse.type = type
                document.addEventListener('mouseup', this.mouseUpHandler)
            },
            mouseUpHandler (e) {
                const endX = e.pageX
                const endY = e.pageY
                const max = Math.max(endX - this.nodeMouse.startX, endY - this.nodeMouse.startY)
                // 移动距离小于 3 像素，认为是点击事件
                if (max < 3) {
                    this.onOpenNodeMenu()
                }
                document.removeEventListener('mouseup', this.mouseUpHandler)
            }
        }
    }
</script>
<style lang="scss">
    .palette-panel {
        position: relative;
        width: 60px;
        height: 100%;
        z-index: 4;
    }
    .palette-container{
        position: relative;
        height: 100%;
        border-right: 1px solid #cacedb;
        background: #ffffff;
        z-index: 3;
        .palette-item {
            padding: 15px 0;
            text-align: center;
            cursor: move;
            user-select: none;
            &:hover {
                .node-type-icon,
                .node-type-text {
                    color: #3a84ff;
                }
                .node-type-text {
                    border-color: #3a84ff;
                }
            }
            &.disabled {
                opacity: 0.3;
                pointer-events: none;
            }
        }
        .palette-with-menu {
            position: relative;
            cursor: pointer;
            &.actived,
            &:hover {
                .node-type-icon {
                    color: #3a84ff;
                }
            }
        }
        .node-type-text {
            display: flex;
            margin: 0 auto;
            font-size: 12px;
            width: 32px;
            height: 32px;
            justify-content: center;
            align-items: center;
            color: #52699d;
            border: 1px solid #546a9e;
            border-radius: 50%;
        }
        .node-type-icon {
            font-size: 32px;
            color: #546a9e;
        }
    }
</style>
