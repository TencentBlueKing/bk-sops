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
    <div class="node-tree-wrapper">
        <NodeTreeItem
            :active-id="activeId"
            :node-list="treeData"
            @click="handleClickNode">
        </NodeTreeItem>
    </div>
</template>
<script>

    import tools from '@/utils/tools.js'
    import NodeTreeItem from './NodeTreeItem'

    export default {
        name: 'NodeTree',
        components: {
            NodeTreeItem
        },
        props: {
            data: {
                type: Array,
                default () {
                    return []
                }
            },
            defaultActiveId: {
                type: String,
                default: ''
            },
            nodeDisplayStatus: {
                type: Object,
                default: {},
                required: true
            }
        },
        data () {
            return {
                activeId: this.defaultActiveId,
                treeData: []
            }
        },
        watch: {
            data: {
                handler (value) {
                    const treeData = tools.deepClone(value)
                    this.nodeAddStatus(this.treeData, this.nodeDisplayStatus.children)
                    this.treeData = treeData
                },
                deep: true,
                immediate: true
            },
            nodeDisplayStatus: {
                handler (val) {
                    this.nodeAddStatus(this.treeData, val.children)
                },
                deep: true,
                immediate: true
            }
        },
        mounted () {
            if (this.defaultActiveId) {
                this.setDefaultActiveId(this.treeData, this.defaultActiveId)
            }
        },
        methods: {
            handleClickNode (node) {
                this.activeId = node.id
                this.$emit('onSelectNode', node)
            },
            nodeAddStatus (treeData = [], states) {
                treeData.forEach(node => {
                    const { id, conditionType, isSubProcess, children } = node
                    if (conditionType) {
                        if (children?.length) {
                            this.nodeAddStatus(children, states)
                        }
                        return
                    }
                    if (!states[id]) return
                    let nodeState = 'READY'
                    nodeState = states[id].skip ? 'SKIP' : states[id].state
                    if (children) {
                        const newStates = isSubProcess ? Object.assign({}, states, states[id].children) : states
                        this.nodeAddStatus(children, newStates)
                    }
                    this.$set(node, 'state', nodeState)
                })
            },
            setDefaultActiveId (treeData = [], id) {
                return treeData.some(item => {
                    if (item.id === id) {
                        return true
                    } else if (item.children?.length) {
                        item.expanded = this.setDefaultActiveId(item.children, id)
                        return item.expanded
                    }
                })
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
.node-tree-wrapper {
    width: 100%;
    padding: 16px 16px 0 8px;
    height: 100%;
    overflow-x: auto;
    @include scrollbar;
}
</style>
