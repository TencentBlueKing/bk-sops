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
            @dynamicLoad="$emit('dynamicLoad', $event)"
            @click="handleClickNode">
        </NodeTreeItem>
    </div>
</template>
<script>

    import NodeTreeItem from './NodeTreeItem'

    export default {
        name: 'NodeTree',
        components: {
            NodeTreeItem
        },
        props: {
            treeData: {
                type: Array,
                default () {
                    return []
                }
            },
            defaultActiveId: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                activeId: this.defaultActiveId
            }
        },
        watch: {
            defaultActiveId: {
                handler (val) {
                    this.activeId = val
                    let nodeId = val.split('-')[0]
                    // 分支条件默认选中特殊处理
                    if (val.split('-').pop() === 'condition') {
                        nodeId = val.split('-').slice(0, -1).join('-')
                        this.activeId = nodeId
                    }
                    this.setDefaultActiveId(this.treeData, nodeId)
                },
                deep: true,
                immediate: true
            }
        },
        methods: {
            handleClickNode (node) {
                this.activeId = node.parentId ? node.id + '-' + node.parentId : node.id
                this.$emit('onSelectNode', node)
            },
            setDefaultActiveId (treeData = [], id) {
                return treeData.some(item => {
                    if (item.id === id) {
                        item.expanded = !!item.isSubProcess
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
    padding: 16px 16px 16px 8px;
    height: 100%;
    overflow-x: auto;
    @include scrollbar;
}
</style>
