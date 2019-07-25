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
    <div class="static-ip">
        <div v-show="!isIpAddingPanelShow" class="ip-list-panel">
            <div class="operation-area">
                <bk-button theme="default" @click="onAddPanelShow" :disabled="!editable">{{i18n.add}}</bk-button>
                <bk-dropdown-menu
                    v-if="isShowQuantity"
                    trigger="click"
                    :disabled="!editable"
                    @show="onDropdownShow"
                    @hide="onDropdownHide">
                    <bk-button theme="default" class="trigger-btn" slot="dropdown-trigger" :disabled="!editable">
                        <span>{{i18n.moreOperations}}</span>
                        <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
                    </bk-button>
                    <div slot="dropdown-content">
                        <div
                            v-for="operation in moreOperations"
                            :key="operation.type"
                            class="operation-btn"
                            @click="onOperationClick(operation.type)">
                            {{operation.name}}
                        </div>
                    </div>
                </bk-dropdown-menu>
                <ip-search-input class="ip-search-wrap" @search="onStaticIpSearch"></ip-search-input>
            </div>
            <div v-if="isShowQuantity" class="selected-num">{{i18n.selected}}
                <span class="total-ip">{{staticIps.length}}</span>
                {{i18n.staticIpNum}}
                <span class="total-not-installed">{{failedAgentLength}}</span>
                {{i18n.num}}
            </div>
            <div class="selected-ip-table-wrap">
                <table class="ip-table">
                    <thead>
                        <tr>
                            <th width="">{{i18n.cloudArea}}</th>
                            <th width="">IP</th>
                            <th width="">{{i18n.status + i18n.error}}</th>
                            <th width="50">{{i18n.operation}}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-if="listInPage.length">
                            <tr v-for="item in listInPage" :key="item.bk_host_d">
                                <td>{{item.cloud[0] && item.cloud[0].bk_inst_name}}</td>
                                <td>{{item.bk_host_innerip}}</td>
                                <td :class="item.agent ? 'agent-normal' : 'agent-failed'">{{item.agent ? 'Agent' + i18n.normal : 'Agent' + i18n.error}}</td>
                                <td>
                                    <a
                                        :class="['remove-ip-btn', { 'disabled': !editable }]"
                                        @click.stop="onRemoveIpClick(item.bk_host_id)">
                                        {{i18n.remove}}
                                    </a>
                                </td>
                            </tr>
                        </template>
                        <tr v-else>
                            <td class="static-ip-empty" colspan="4">
                                <span v-if="!isSearchMode && editable">
                                    {{i18n.noDataClick}}
                                    <span class="add-ip-btn" @click="onAddPanelShow">{{i18n.add}}</span>
                                    {{i18n.server}}
                                </span>
                                <span v-else>{{i18n.noData}}</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <div class="table-pagination" v-if="isPaginationShow">
                    <bk-pagination
                        :current.sync="currentPage"
                        :count="totalCount"
                        :limit="listCountPerPage"
                        :limit-list="[15,20,30]"
                        :show-limit="false"
                        @change="onPageChange">
                    </bk-pagination>
                </div>
                <span v-show="dataError" class="common-error-tip error-info">{{i18n.notEmpty}}</span>
            </div>
        </div>
        <static-ip-adding-panel
            v-if="isIpAddingPanelShow"
            :static-ip-list="staticIpList"
            :static-ips="staticIps"
            @onAddIpConfirm="onAddIpConfirm"
            @onAddIpCancel="onAddIpCancel">
        </static-ip-adding-panel>
    </div>
</template>
<script>
    import '@/utils/i18n.js' // ip选择器兼容标准运维国际化

    import StaticIpAddingPanel from './StaticIpAddingPanel.vue'
    import IpSearchInput from './IpSearchInput.vue'

    const i18n = {
        copyIp: gettext('复制IP'),
        copyAgentIp: gettext('复制Agent未安装IP'),
        clearIp: gettext('清空IP'),
        clearFailedAgentIp: gettext('清空Agent未安装IP'),
        add: gettext('添加'),
        moreOperations: gettext('更多操作'),
        selected: gettext('已选择'),
        staticIpNum: gettext('个静态IP(未安装agent'),
        num: gettext('个)'),
        cloudArea: gettext('云区域'),
        status: gettext('状态'),
        error: gettext('异常'),
        operation: gettext('操作'),
        remove: gettext('移除'),
        normal: gettext('正常'),
        noDataClick: gettext('无数据，点击'),
        server: gettext('服务器'),
        noData: gettext('无数据'),
        notEmpty: gettext('必填项')
    }

    export default {
        name: 'StaticIp',
        components: {
            StaticIpAddingPanel,
            IpSearchInput
        },
        props: ['editable', 'staticIpList', 'staticIps'],
        data () {
            const listCountPerPage = 5
            const totalPage = Math.ceil(this.staticIps.length / listCountPerPage)
            return {
                isDropdownShow: false,
                isIpAddingPanelShow: false,
                isSearchMode: false,
                copyText: '',
                isPaginationShow: totalPage > 1,
                currentPage: 1,
                totalCount: this.staticIps.length,
                totalPage: totalPage,
                listCountPerPage: listCountPerPage,
                listInPage: this.staticIps.slice(0, listCountPerPage),
                dataError: false,
                moreOperations: [
                    {
                        type: 'copyIp',
                        name: i18n.copyIp
                    },
                    {
                        type: 'copyAgentIp',
                        name: i18n.copyAgentIp
                    },
                    {
                        type: 'clearIp',
                        name: i18n.clearIp
                    },
                    {
                        type: 'clearFailedAgentIp',
                        name: i18n.clearFailedAgentIp
                    }
                ],
                i18n
            }
        },
        computed: {
            failedAgentLength () {
                return this.staticIps.filter(item => !item.agent).length
            },
            isShowQuantity () {
                return this.staticIps.length
            }
        },
        watch: {
            staticIps (val) {
                this.setPanigation(val)
                if (this.staticIps.length !== 0) {
                    this.dataError = false
                }
            }
        },
        methods: {
            setPanigation (list = []) {
                this.listInPage = list.slice(0, this.listCountPerPage)
                this.totalPage = Math.ceil(list.length / this.listCountPerPage)
                this.isPaginationShow = this.totalPage > 1
                this.currentPage = 1
            },
            onAddPanelShow () {
                if (!this.editable) {
                    return
                }
                this.isIpAddingPanelShow = true
            },
            handleIpCopy (ipStr) {
                this.copyText = ipStr
                document.addEventListener('copy', this.copyHandler)
                document.execCommand('copy')
                document.removeEventListener('copy', this.copyHandler)
                this.copyText = ''
            },
            copyHandler (e) {
                e.clipboardData.setData('text/html', this.copyText)
                e.clipboardData.setData('text/plain', this.copyText)
                e.preventDefault()
            },
            copyIp () {
                const ipStr = this.staticIps.map(item => item.bk_host_innerip).join(',')
                this.handleIpCopy(ipStr)
            },
            copyAgentIp () {
                const ipStr = this.staticIps.filter(item => !item.agent).map(d => d.bk_host_innerip).join(',')
                this.handleIpCopy(ipStr)
            },
            clearIp () {
                this.$emit('change', [])
            },
            clearFailedAgentIp () {
                const staticIps = this.staticIps.filter(item => !!item.agent)
                this.$emit('change', staticIps)
            },
            onDropdownShow () {
                this.isDropdownShow = true
            },
            onDropdownHide () {
                this.isDropdownShow = false
            },
            onStaticIpSearch (keyword) {
                if (keyword) {
                    const keyArr = keyword.split(',')
                    const list = this.staticIps.filter(item => {
                        return keyArr.some(str => item.bk_host_innerip.indexOf(str) > -1)
                    })
                    this.setPanigation(list)
                    this.isSearchMode = true
                } else {
                    this.setPanigation(this.staticIps)
                    this.isSearchMode = false
                }
            },
            onOperationClick (type) {
                this[type] && this[type]()
            },
            onRemoveIpClick (id) {
                if (!this.editable) {
                    return
                }
                const index = this.staticIps.findIndex(item => item.bk_host_id === id)
                const staticIps = this.staticIps.slice(0)
                staticIps.splice(index, 1)
                this.$emit('change', staticIps)
            },
            onAddIpConfirm (data) {
                this.$emit('change', data)
                this.isIpAddingPanelShow = false
            },
            onAddIpCancel () {
                this.isIpAddingPanelShow = false
            },
            onPageChange (page) {
                this.currentPage = page
                this.listInPage = this.staticIps.slice((page - 1) * this.listCountPerPage, page * this.listCountPerPage)
            },
            validate () {
                if (this.staticIps.length) {
                    this.dataError = false
                    return true
                } else {
                    this.dataError = true
                    this.onAddIpCancel()
                    return false
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
.operation-area {
    position: relative;
    margin: 20px 0;
    .bk-dropdown-menu, .trigger-btn {
        width: 162px;
        padding: 0px;
    }
}
.operation-btn {
    padding: 5px 8px;
    color: #3a84ff;
    font-size: 14px;
    cursor: pointer;
    &:hover {
        background: #ebf4ff;
    }
}
.selected-num {
    margin-bottom: 20px;
    font-size: 14px;
    .total-ip {
        color: #3a84ff;
    }
    .total-not-installed {
        color: #ea3636;
    }
}
/deep/.bk-button .bk-icon {
    margin-left: 55px;
}
.ip-search-wrap {
    position: absolute;
    top: 0;
    right: 0;
    width: 50%;
}
.ip-table {
    width: 100%;
    border: 1px solid #dde4eb;
    border-collapse: collapse;
    tr {
        border-bottom: 1px solid #dde4eb;
    }
    th {
        color: #313238;
    }
    th,td {
        padding: 12px 10px;
        line-height: 1;
        font-size: 12px;
        font-weight: normal;
        text-align: left;
        &.agent-normal {
            color: #22a945;
        }
        &.agent-failed {
            color: #ea3636;
        }
    }
    .remove-ip-btn {
        color: #3a84ff;
        cursor: pointer;
        &.disabled {
            color: #cccccc;
            cursor: not-allowed;
        }
    }
    .static-ip-empty {
        height: 214px;
        text-align: center;
        color: #c4c6cc;
        .add-ip-btn {
            margin: 0 -2px 0 -2px;
            color: #3a84ff;
            cursor: pointer;
        }
    }
}
.table-pagination {
    margin-top: 20px;
    .bk-page {
        justify-content: flex-end;
        /deep/ .page-item {
            min-width: 30px;
            height: 30px;
            line-height: 30px;
            font-size: 12px;
        }
    }
}
</style>
