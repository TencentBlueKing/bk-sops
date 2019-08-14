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
            <div class="palette-item" data-type="startpoint">
                <div class="node-type-text start-point">{{ i18n.start }}</div>
            </div>
            <div class="palette-item" data-type="endpoint">
                <div class="node-type-text end-point">{{ i18n.end }}</div>
            </div>
            <div class="palette-item" data-type="parallelgateway">
                <div class="node-type-icon common-icon-node-parallelgateway"></div>
            </div>
            <div class="palette-item" data-type="branchgateway">
                <div class="node-type-icon common-icon-node-branchgateway"></div>
            </div>
            <div class="palette-item" data-type="convergegateway">
                <div class="node-type-icon common-icon-node-convergegateway"></div>
            </div>
            <div
                :class="['palette-item', 'palette-with-menu', { actived: activeNodeListType === 'tasknode' }]"
                data-type="tasknode"
                @mousedown="onToggleNodeMenu('tasknode')">
                <div class="node-type-icon common-icon-node-tasknode"></div>
            </div>
            <div
                :class="['palette-item', 'palette-with-menu', { actived: activeNodeListType === 'subflow' }]"
                data-type="subflow"
                @click.native="onToggleNodeMenu('subflow')">
                <div class="node-type-icon common-icon-node-subflow"></div>
            </div>
        </div>
        <node-menu
            :show-node-menu="showNodeMenu"
            :is-fixed-node-menu="isFixedNodeMenu"
            :active-node-list-type="activeNodeListType"
            :nodes="nodes"
            @onHideNodeMenu="onHideNodeMenu"
            @onToggleNodeMenuFixed="onToggleNodeMenuFixed">
        </node-menu>
    </div>
</template>
<script>
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
            }
        },
        data () {
            return {
                activeNodeListType: '',
                showNodeMenu: false,
                isFixedNodeMenu: false,
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
        mounted () {
            this.$emit('registerPaletteEvent')
        },
        methods: {
            onToggleNodeMenu (type) {
                debugger
                let showNodeMenu
                let activedType
                if (this.isFixedNodeMenu) {
                    showNodeMenu = true
                    activedType = type
                } else {
                    if (this.activeNodeListType === type) {
                        showNodeMenu = false
                        activedType = ''
                    } else {
                        showNodeMenu = true
                        activedType = type
                    }
                }
                debugger
                this.showNodeMenu = showNodeMenu
                this.activeNodeListType = activedType
            },
            onToggleNodeMenuFixed (val) {
                this.isFixedNodeMenu = val
            },
            onHideNodeMenu () {
                this.showNodeMenu = false
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
        background: #f2f2f2;
        border-right: 1px solid #dddddd;
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
        }
        .palette-with-menu {
            position: relative;
            cursor: pointer;
            &.actived,
            &:hover {
                background: #ffffff;
            }
            &::after {
                position: absolute;
                bottom: 0;
                right: 0;
                content: '';
                width: 0;
                height: 0;
                border-style: solid;
                border-width: 0 0 8px 8px;
                border-color: transparent transparent #546a9e transparent;
            }
        }
        .node-type-text {
            margin: 0 auto;
            font-size: 12px;
            width: 32px;
            height: 32px;
            line-height: 32px;
            color: #52699d;
            border: 1px solid #546a9e;
            border-radius: 50%;
        }
        .node-type-icon {
            font-size: 32px;
            color: #52699d;
        }
    }
</style>
