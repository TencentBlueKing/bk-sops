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
    <div class="dynamic-ip">
        <div class="dynamic-ip-select">
            <div class="topo-tree">
                <ip-search-input
                    class="ip-search-wrap"
                    :placeholder="$t('搜索节点')"
                    :editable="editable"
                    @search="onTopoSearch">
                </ip-search-input>
                <div :class="['tree-wrap', { 'is-view': !editable }]">
                    <bk-big-tree
                        v-if="topoList.length"
                        ref="topoTree"
                        show-checkbox
                        :height="360"
                        :check-strictly="true"
                        :options="{ idKey: 'uniqueId', nameKey: 'label' }"
                        :data="topoList"
                        :default-checked-nodes="selectedIps"
                        :filter-method="filterNode"
                        @check-change="onNodeCheckClick">
                    </bk-big-tree>
                    <div v-else class="dynamic-ip-empty">{{$t('无数据')}}</div>
                </div>
            </div>
            <div class="selected-ips">
                <div class="ip-num">{{$t('已选择')}}
                    <span>{{dynamicIps.length}}</span>
                    {{$t('个节点')}}
                </div>
                <div class="ip-list">
                    <div
                        :class="['ip-item', { 'disabled': !editable }]"
                        v-for="item in selectedIpsPath"
                        :key="item.key">
                        <div class="ip-path" v-bk-overflow-tips>{{ item.namePath }}</div>
                        <span class="invalid" v-if="item.diff">{{ $t('失效') }}</span>
                        <i v-if="editable" class="common-icon-dark-circle-close" @click="onDeleteSelected(item.key, item.diff)"></i>
                    </div>
                </div>
            </div>
        </div>
        <span v-show="dataError" class="common-error-tip error-info">{{$t('必填项')}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js' // ip选择器兼容标准运维国际化

    import IpSearchInput from './IpSearchInput.vue'

    export default {
        name: 'DynamicIp',
        components: {
            IpSearchInput
        },
        props: ['editable', 'dynamicIpList', 'dynamicIps'],
        data () {
            return {
                lastSelectedNodes: [],
                selectedNodeList: [],
                checkedNode: null,
                topoList: this.transPrimaryToTree(this.dynamicIpList),
                searchWord: '',
                selectedList: this.dynamicIps.slice(0),
                selectedIps: this.dynamicIps.map(item => `${item.bk_inst_id}_${item.bk_obj_id}`),
                selectedIpsPath: [],
                dataError: false,
                matchedList: []
            }
        },
        watch: {
            dynamicIpList (val, old) {
                this.topoList = this.transPrimaryToTree(val)
                this.setSelectedIpsPath()
                this.$nextTick(() => {
                    this.selectedIps.forEach(item => {
                        // 清除默认选中 改为通过点击的方式选中
                        this.$refs.topoTree.setChecked(item, { checked: false })
                        this.getCheckedNodeInfo(this.topoList, item)
                        if (this.checkedNode) {
                            if (this.checkedNode.id !== this.checkedNode.uniqueId) {
                                this.checkedNode.id = this.checkedNode.uniqueId
                                this.onNodeCheckClick(this.selectedIps, this.checkedNode, false)
                            } else {
                                this.selectedNodeList.push(item)
                            }
                        }
                    })
                })
            },
            dynamicIps (val) {
                this.selectedList = val.slice(0)
                this.selectedIps = val.map(item => `${item.bk_inst_id}_${item.bk_obj_id}`)
                this.setSelectedIpsPath()
                if (val.length !== 0) {
                    this.dataError = false
                }
            }
        },
        methods: {
            /**
             * 原始拓扑树结构转换为 tree 组件结构
             */
            transPrimaryToTree (data, isParentChecked = false) {
                const list = []
                data.map(d => {
                    const checked = !!this.dynamicIps.find(item => item.bk_inst_id === d.bk_inst_id && item.bk_obj_id === d.bk_obj_id)
                    const item = {
                        label: d.bk_inst_name,
                        bk_inst_id: d.bk_inst_id,
                        uniqueId: `${d.bk_inst_id}_${d.bk_obj_id}`,
                        bk_obj_id: d.bk_obj_id,
                        disabled: isParentChecked // tips：tree 组件配置节点 disabled、checked 属性不生效，需手动设置组件修复
                    }
                    if (Array.isArray(d.child)) {
                        item.children = this.transPrimaryToTree(d.child, checked)
                    }
                    list.push(item)
                })
                return list
            },
            /**
             * 遍历获取子节点列表
             */
            traverseNodesToList (nodes) {
                let list = []
                nodes.forEach(item => {
                    list.push(item.id)
                    if (item.children && item.children.length > 0) {
                        list = list.concat(this.traverseNodesToList(item.children))
                    }
                })
                return list
            },
            getNodeNamePath (node) {
                let namePath = node.data.label
                if (node.parent) {
                    const parentName = this.getNodeNamePath(node.parent)
                    namePath = parentName + '/' + namePath
                }
                return namePath
            },
            setSelectedIpsPath () {
                if (this.dynamicIpList.length > 0) {
                    this.$nextTick(() => {
                        const selectedIpsPath = []
                        this.selectedIps.forEach(key => {
                            const selectedNode = this.$refs.topoTree.getNodeById(key)
                            if (selectedNode) {
                                const namePath = this.getNodeNamePath(selectedNode)
                                selectedIpsPath.push({ key, namePath })
                            } else {
                                selectedIpsPath.push({ key, namePath: key.split('_').join('/'), diff: true })
                            }
                        })
                        this.selectedIpsPath = selectedIpsPath
                    })
                }
            },
            onTopoSearch (keyword) {
                this.matchedList = []
                this.$refs.topoTree.filter(String(keyword).toLowerCase())
            },
            filterNode (value, node) {
                if (!value) return true
                const { data, id, level, children, parent } = node
                const keyword = String(data.label).toLowerCase()
                if (keyword.indexOf(value) > -1) {
                    // 当节点匹配到以后, 如果有子节点则记录节点id, level
                    if (children.length) {
                        this.matchedList.push({ id, level })
                    }
                    return true
                } else {
                    // 当节点没有匹配上, 但父节点匹配上时, 父节点底下所有子孙节点默认显示
                    const matchParent = this.matchedList.find(item => item.id === parent.id && item.level === parent.level)
                    if (matchParent) {
                        if (children.length) {
                            this.matchedList.push({ id, level })
                        }
                        return true
                    }
                }
            },
            onNodeCheckClick (selectedNodes, node, update = true) {
                const checkedList = selectedNodes.slice(0)
                if (checkedList.length >= this.lastSelectedNodes.length) {
                    this.selectedNodeList.push(node.id)
                    if (node.children && node.children.length) {
                        this.setSelectedNodeList(node.children)
                    }
                } else {
                    const index = this.selectedNodeList.findIndex(item => item === node.id)
                    if (index > -1) {
                        this.selectedNodeList.splice(index, 1)
                    } else {
                        if (node.children && node.children.length) {
                            this.setSelectedNodeList(node.children)
                        }
                    }
                }
                this.lastSelectedNodes = checkedList

                const isChecked = selectedNodes.includes(node.id)
                if (node.children && node.children.length) {
                    this.changeChildrenNodeState(node, checkedList, isChecked)
                }

                const selectedList = this.selectedNodeList.map(uniqueId => {
                    const [bk_inst_id, bk_obj_id] = uniqueId.split('_')
                    return { bk_inst_id: Number(bk_inst_id), bk_obj_id }
                })
                checkedList.forEach(id => {
                    this.$refs.topoTree.setChecked(id, { checked: true })
                })
                if (update) { // 初始化时不更新选中数据
                    this.$emit('change', selectedList)
                    this.validate()
                }
            },
            changeChildrenNodeState (node, checkedList, isChecked) {
                node.children.forEach(item => {
                    const nodeId = item.uniqueId || item.id
                    if (isChecked) {
                        const index = checkedList.findIndex(id => id === nodeId)
                        if (index > -1) {
                            checkedList.splice(index, 1)
                            this.$refs.topoTree.setChecked(nodeId, { checked: false })
                        }
                    }
                    this.$refs.topoTree.setDisabled(nodeId, { disabled: isChecked })
                    if (item.children && item.children.length) {
                        this.changeChildrenNodeState(item, checkedList, isChecked)
                    }
                })
            },
            onDeleteSelected (key) {
                if (!this.editable) return
                const index = this.selectedNodeList.findIndex(item => item === key)
                if (index > -1) {
                    this.selectedNodeList.splice(index, 1)
                }
                const selectedList = this.selectedNodeList.map(uniqueId => {
                    const [bk_inst_id, bk_obj_id] = uniqueId.split('_')
                    return { bk_inst_id: Number(bk_inst_id), bk_obj_id }
                })
                this.lastSelectedNodes = []
                this.checkedNode = null
                this.getCheckedNodeInfo(this.topoList, key)
                if (this.checkedNode && this.checkedNode.children && this.checkedNode.children.length) {
                    this.setChildrenNodeState(this.checkedNode.children)
                }
                this.$refs.topoTree.setChecked(key, { checked: false })
                this.$emit('change', selectedList)
                this.validate()
            },
            getCheckedNodeInfo (data, id) {
                for (let i = 0; i < data.length; i++) {
                    const item = data[i]
                    if (item.uniqueId === id) {
                        this.checkedNode = item
                        return
                    } else if (item.children && item.children.length) {
                        this.getCheckedNodeInfo(item.children, id)
                    }
                }
            },
            setChildrenNodeState (data) {
                data.forEach(item => {
                    this.$refs.topoTree.setDisabled(item.uniqueId, { disabled: false })
                    if (item.children && item.children.length) {
                        this.setChildrenNodeState(item.children)
                    }
                })
            },
            setSelectedNodeList (data) {
                data.forEach(item => {
                    const uniqueId = item.uniqueId || item.data.uniqueId
                    if (uniqueId) {
                        const idx = this.selectedNodeList.findIndex(val => val === uniqueId)
                        if (idx > -1) {
                            this.selectedNodeList.splice(idx, 1)
                        }
                    }
                    if (item.children && item.children.length) {
                        this.setSelectedNodeList(item.children)
                    }
                })
            },
            validate () {
                if (this.dynamicIps.length) {
                    this.dataError = false
                    return true
                } else {
                    this.dataError = true
                    return false
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
.dynamic-ip-select {
    border: 1px solid #ddebe4;
    overflow: hidden;
}
.topo-tree {
    float: left;
    padding: 8px;
    width: 50%;
    border-right: 1px solid #ddebe4;
}
.selected-ips {
    float: left;
    padding: 8px 0;
    width: 50%;
    .ip-num {
        margin: 8px 0 12px;
        padding: 0 8px;
        font-size: 12px;
        color: #313238;
        & > span {
            color: #3a84ff;
        }
    }
    .ip-item {
        position: relative;
        padding: 0 28px 0 8px;
        line-height: 32px;
        display: flex;
        align-items: center;
        .ip-path {
            overflow:hidden;
            text-overflow:ellipsis;
            white-space:nowrap;
        }
        .invalid {
            flex-shrink: 0;
            height: 20px;
            line-height: 15px;
            padding: 2px 5px;
            margin-left: 5px;
            transform: scale(0.8);
            color: #63656e;
            background: #f0f1f5;
            border: 1px solid #c4c6cc;
            border-radius: 2px;
        }
        &.disabled {
            color: #ccc;
            cursor: not-allowed;
            i {
                cursor: not-allowed;
                &:hover {
                    color: #dcdee6;
                }
            }
            .invalid {
                color: #ccc;
                background-color: #fafbfd;
                border-color: #dcdee5;
            }
        }
    }
    .common-icon-dark-circle-close {
        position: absolute;
        right: 12px;
        top: 10px;
        font-size: 12px;
        color: #dcdee6;
        cursor: pointer;
        &:hover {
            color: #3a84ff;
        }
    }
}
.ip-search-wrap {
    position: relative;
    margin-bottom: 10px;
    width: 100%;
    /deep/ .search-input {
        width: 100%;
    }
}
.tree-wrap,
.ip-list {
    height: 360px;
    overflow: auto;
    &::-webkit-scrollbar {
        width: 4px;
        height: 4px;
        &-thumb {
            border-radius: 20px;
            background: #a5a5a5;
            box-shadow: inset 0 0 6px hsla(0,0%,80%,.3);
        }
    }
}
.is-view {
    /deep/ .bk-big-tree {
        .bk-scroll-item {
            .node-checkbox {
                border-color: #dcdee5;
            }
            &::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                z-index: 3;
                height: 100%;
                width: 100%;
                cursor: not-allowed;
            }
        }
    }
}
.el-tree {
    background: inherit;
    /deep/ .el-tree-node__label {
        padding-left: 4px;
    }
}
/deep/ .bk-big-tree-node .node-content {
    font-size: 12px;
}
.dynamic-ip-empty {
    height: 360px;
    line-height: 360px;
    vertical-align: middle;
    text-align: center;
    font-size: 12px;
    color: #c4c6cc;
}
</style>
