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
    <ul :class="['node-tree', 'tree-level-' + level]">
        <li v-for="(item, key) in data" :key="key" class="tree-item">
            <h4
                :class="{
                    'node-name': true,
                    'actived': getNodeActivedState(item.id)
                }"
                @click.stop="onSelectNode(item, true)">
                <span class="node-icon">
                    <i :class="item.children ? 'common-icon-node-subflow' : 'common-icon-node-tasknode'"></i>
                </span>
                <span class="name" :title="item.name">{{item.name}}</span>
            </h4>
            <NodeTree
                v-if="item.children"
                class="sub-tree"
                :data="item.children"
                :selected-flow-path="selectedFlowPath"
                :heirarchy="heirarchy ? `${heirarchy}.${item.id}` : String(item.id)"
                :level="level + 1"
                @onSelectNode="onSelectNode">
            </NodeTree>
        </li>
    </ul>
</template>
<script>
    import '@/utils/i18n.js'
    export default {
        name: 'NodeTree',
        props: {
            data: {
                type: Array,
                default () {
                    return []
                }
            },
            selectedFlowPath: {
                type: Array,
                default () {
                    return []
                }
            },
            heirarchy: {
                type: String,
                default: ''
            },
            level: {
                type: Number,
                default: 1
            }
        },
        methods: {
            getNodeActivedState (id) {
                const len = this.selectedFlowPath.length
                if (this.selectedFlowPath[len - 1].id === id) {
                    return true
                }
                return false
            },
            onSelectNode (node, isClick, type) {
                let nodeHeirarchy = node
                const nodeType = node.children ? 'subflow' : 'tasknode'
                if (isClick) {
                    nodeHeirarchy = this.heirarchy ? `${this.heirarchy}.${node.id}` : String(node.id)
                }
                this.$emit('onSelectNode', nodeHeirarchy, false, nodeType)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.node-tree {
    display: inline-block;
    width: 100%;
    &.tree-level-1 {
        overflow-x: auto;
        @include scrollbar;
    }
    &.sub-tree {
        .tree-item {
            position: relative;
            margin-left: 20px;
            &:last-child:before {
                height: 22px;
            }
            &:before {
                content: '';
                position: absolute;
                left: 8px;
                top: -6px;
                height: 100%;
                border-left: 1px dashed $commonBorderColor;
            }
            &:after {
                content: '';
                position: absolute;
                left: 12px;
                top: 16px;
                width: 8px;
                border-bottom: 1px dashed $commonBorderColor;
            }
        }
    }
    .node-name {
        display: inline-block;
        margin: 0;
        padding-left: 20px;
        width: 140px;
        height: 30px;
        line-height: 30px;
        font-size: 12px;
        font-weight: normal;
        color: $greyDefault;
        white-space: nowrap;
        cursor: pointer;
        &.actived {
            color: $blueDefault;
        }
        &:hover {
            color: $blueDefault;
        }
        .node-icon {
            float: left;
            font-size: 16px;
            font-weight: bold;
            .common-icon-node-subflow,.common-icon-node-tasknode{
                font-weight: bold;
            }
        }
        .name {
            float: left;
            margin-left: 4px;
            max-width: 90px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            vertical-align: -10px;
        }
    }
}
</style>
