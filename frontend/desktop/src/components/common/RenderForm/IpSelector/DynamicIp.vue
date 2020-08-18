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
    <div class="dynamic-ip">
        <div class="dynamic-ip-select">
            <div class="topo-tree">
                <ip-search-input
                    class="ip-search-wrap"
                    :placeholder="i18n.searchNode"
                    @search="onTopoSearch">
                </ip-search-input>
                <div class="tree-wrap">
                    <el-tree
                        v-if="topoList.length"
                        ref="topoTree"
                        default-expand-all
                        show-checkbox
                        check-strictly
                        node-key="uniqueId"
                        :data="topoList"
                        :default-checked-keys="selectedIps"
                        :filter-node-method="filterNode"
                        @check="onNodeCheckClick">
                    </el-tree>
                    <div v-else class="dynamic-ip-empty">{{i18n.noData}}</div>
                </div>
            </div>
            <div class="selected-ips">
                <div class="ip-num">{{i18n.selected}}
                    <span>{{dynamicIps.length}}</span>
                    {{i18n.dynamicNum}}
                </div>
                <div class="ip-list">
                    <div
                        class="ip-item"
                        v-for="item in selectedIpsPath"
                        :key="item.key">
                        {{ item.namePath }}
                        <i class="common-icon-dark-circle-close" @click="onDeleteSelected(item.key)"></i>
                    </div>
                </div>
            </div>
        </div>
        <span v-show="dataError" class="common-error-tip error-info">{{i18n.notEmpty}}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js' // ip选择器兼容标准运维国际化

    import IpSearchInput from './IpSearchInput.vue'

    const i18n = {
        selected: gettext('已选择'),
        dynamicNum: gettext('个节点'),
        searchNode: gettext('搜索节点'),
        noData: gettext('无数据'),
        notEmpty: gettext('必填项')
    }

    export default {
        name: 'DynamicIp',
        components: {
            IpSearchInput
        },
        props: ['editable', 'dynamicIpList', 'dynamicIps'],
        data () {
            return {
                topoList: this.transPrimaryToTree(this.dynamicIpList),
                searchWord: '',
                selectedList: this.dynamicIps.slice(0),
                selectedIps: this.dynamicIps.map(item => `${item.bk_inst_id}_${item.bk_obj_id}`),
                selectedIpsPath: [],
                dataError: false,
                i18n
            }
        },
        watch: {
            dynamicIpList (val) {
                this.topoList = this.transPrimaryToTree(val)
                this.setSelectedIpsPath()
            },
            dynamicIps (val) {
                this.selectedList = val.slice(0)
                this.selectedIps = val.map(item => `${item.bk_inst_id}_${item.bk_obj_id}`)
                this.topoList = this.transPrimaryToTree(this.dynamicIpList)
                this.setSelectedIpsPath()
                if (val.length !== 0) {
                    this.dataError = false
                }
            }
        },
        methods: {
            transPrimaryToTree (data, isParentDisabled = false) {
                const list = []
                data.map(d => {
                    const disabled = !this.editable || isParentDisabled
                    const checked = this.dynamicIps.findIndex(item => {
                        return item.bk_inst_id === d.bk_inst_id && item.bk_obj_id === d.bk_obj_id
                    }) > -1

                    const item = {
                        label: d.bk_inst_name,
                        bk_inst_id: d.bk_inst_id,
                        uniqueId: `${d.bk_inst_id}_${d.bk_obj_id}`,
                        bk_obj_id: d.bk_obj_id,
                        disabled
                    }
                    if (Array.isArray(d.child)) {
                        item.children = this.transPrimaryToTree(d.child, isParentDisabled || checked)
                    }
                    list.push(item)
                })
                return list
            },
            getNodeNamePath (node, name = '') {
                const label = node.data.label
                if (node.parent) {
                    const nameStr = name ? `/${name}` : name
                    return this.getNodeNamePath(node.parent, label) + nameStr
                }
                return name
            },
            setSelectedIpsPath () {
                if (this.dynamicIpList.length > 0) {
                    this.$nextTick(() => {
                        const selectedIpsPath = []
                        this.selectedIps.forEach(key => {
                            const selectedNode = this.$refs.topoTree.getNode(key)
                            const namePath = this.getNodeNamePath(selectedNode)
                            selectedIpsPath.push({ key, namePath })
                        })
                        this.selectedIpsPath = selectedIpsPath
                    })
                }
            },
            onTopoSearch (keyword) {
                this.$refs.topoTree.filter(keyword)
            },
            filterNode (value, data) {
                if (!value) return true
                return data.label.indexOf(value) > -1
            },
            onNodeCheckClick (node, checkData) {
                const checkedNodes = checkData.checkedNodes.slice(0)
                const nodeChecking = checkData.checkedKeys.indexOf(node.uniqueId) > -1
                if (node.children && node.children.length && nodeChecking) {
                    this.unCheckChildrenNode(node, checkedNodes)
                }

                const selectedList = checkedNodes.map(node => {
                    return {
                        bk_inst_id: node.bk_inst_id,
                        bk_obj_id: node.bk_obj_id
                    }
                })

                this.$emit('change', selectedList)
                this.validate()
            },
            unCheckChildrenNode (node, checkedNodes) {
                node.children.forEach(item => {
                    const index = this.selectedIps.indexOf(item.uniqueId)
                    if (index > -1) {
                        const checkedIndex = checkedNodes.findIndex(n => item.uniqueId === n.uniqueId)
                        checkedNodes.splice(checkedIndex, 1)
                    }
                    if (item.children && item.children.length) {
                        this.unCheckChildrenNode(item, checkedNodes)
                    }
                })
            },
            onDeleteSelected (key) {
                const selectedList = this.selectedList.filter(item => {
                    return `${item.bk_inst_id}_${item.bk_obj_id}` !== key
                })
                this.$emit('change', selectedList)
                this.validate()
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
.el-tree {
    background: inherit;
    /deep/ .el-tree-node__label {
        padding-left: 4px;
    }
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
