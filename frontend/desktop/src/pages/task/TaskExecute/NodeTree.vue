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
    <div class="node-bk-tree">
        <bk-tree
            class="node-tree"
            ref="bkTree"
            :data="treeData"
            :show-icon="showIcon"
            :node-key="'id'"
            :has-border="true"
            @on-click="onSelectNode">
        </bk-tree>
    </div>
</template>
<script>
    import { bkTree } from 'bk-magic-vue'
    import tools from '@/utils/tools.js'
    export default {
        name: 'NodeTree',
        components: {
            bkTree
        },
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
            },
            defaultActiveId: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                treeData: [],
                showIcon: false
            }
        },
        watch: {
            data: {
                handler () {
                    this.treeData = tools.deepClone(this.data)
                    if (this.defaultActiveId) {
                        this.setDefaultActiveId(this.treeData, this.defaultActiveId)
                    }
                },
                deep: true,
                immediate: true
            }
        },
        methods: {
            setDefaultActiveId (nodes, id) {
                nodes.forEach(node => {
                    if (node.id === id) {
                        node.selected = true
                        return
                    }
                    if (node.children) {
                        this.setDefaultActiveId(node.children, id)
                    }
                })
            },
            getNodeActivedState (id) {
                const len = this.selectedFlowPath.length
                if (this.selectedFlowPath[len - 1].id === id) {
                    return true
                }
                return false
            },
            onSelectNode (node, isClick, type) {
                const nodeType = node.children ? 'subflow' : 'tasknode'
                let rootNode = node
                let nodeHeirarchy = ''
                while (rootNode.parent) {
                    if (nodeHeirarchy) {
                        nodeHeirarchy += '.' + rootNode.parent.id
                    } else {
                        nodeHeirarchy += rootNode.parent.id
                    }
                    rootNode = rootNode.parent
                }
                const selectNodeId = node.id
                this.$emit('onSelectNode', nodeHeirarchy, selectNodeId, nodeType)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.node-bk-tree{
    display: inline-block;
    width: 229px;
    min-width: 229px;
    padding: 24px 8px 0;
}
.node-tree {
    height: 100%;
    white-space: nowrap;
    overflow-x: auto;
    @include scrollbar;
    /deep/.tree-drag-node {
        padding-bottom: 17px;
    }
    /deep/.bk-icon {
            margin-right: 8px;
    }
}
</style>
