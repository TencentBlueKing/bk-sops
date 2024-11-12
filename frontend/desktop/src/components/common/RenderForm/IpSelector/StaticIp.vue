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
    <div class="static-ip">
        <div v-show="!isIpAddingPanelShow" class="ip-list-panel">
            <div :class="['operation-area', { 'is-view': !editable }]">
                <bk-button theme="default" size="small" :disabled="!editable" style="margin-left: 4px;" @click="onAddPanelShow('select')">{{$t('选择添加')}}</bk-button>
                <bk-button theme="default" size="small" :disabled="!editable" style="margin-left: 4px;" @click="onAddPanelShow('manual')">{{$t('手动添加')}}</bk-button>
                <template v-if="staticIps.length">
                    <bk-dropdown-menu
                        trigger="click"
                        :disabled="!editable"
                        @show="onDropdownShow"
                        @hide="onDropdownHide">
                        <bk-button theme="default" size="small" class="trigger-btn" slot="dropdown-trigger" :disabled="!editable">
                            <span>{{$t('批量操作')}}</span>
                            <i :class="['bk-icon icon-angle-down',{ 'icon-flip': isDropdownShow }]"></i>
                        </bk-button>
                        <div slot="dropdown-content">
                            <div
                                v-for="operation in operations"
                                :key="operation.type"
                                class="operation-btn"
                                @click="onOperationClick(operation)">
                                {{operation.name}}
                            </div>
                        </div>
                    </bk-dropdown-menu>
                    <ip-search-input
                        ref="ipSearchInput"
                        :class="['ip-search-wrap', { 'static-ip-unfold': isUnfold }]"
                        :editable="editable"
                        @focus="onStaticIpFocus"
                        @search="onStaticIpSearch">
                    </ip-search-input>
                    <span v-if="isUnfold" @click="isUnfold = false" class="return-text">{{ $t('返回') }}</span>
                </template>
            </div>
            <div class="selected-ip-table-wrap">
                <IpSelectorTable
                    :editable="editable"
                    :is-search-mode="isSearchMode"
                    :static-ip-list="staticIpList"
                    :static-ip-table-config="staticIpTableConfig"
                    @onAddPanelShow="onAddPanelShow"
                    @onTableConfigChange="onTableConfigChange"
                    @onRemoveIpClick="onRemoveIpClick">
                </IpSelectorTable>
                <div class="table-footer">
                    <div v-if="staticIps.length" class="selected-num">{{$t('共')}}
                        <span class="total-ip">{{staticIps.length}}</span>
                        {{$t('个静态IP，')}}
                        {{$t('其中')}}
                        <span class="total-not-installed">{{abnormalLength}}</span>
                        {{$t('个')}}{{$t('异常')}}
                    </div>
                    <div class="table-pagination">
                        <bk-pagination
                            size="small"
                            align="right"
                            v-bind="pagination"
                            :limit-list="[pagination.limit]"
                            :show-limit="false"
                            @change="onPageChange">
                        </bk-pagination>
                    </div>
                </div>
                <span v-show="dataError" class="common-error-tip error-info">{{$t('必填项')}}</span>
            </div>
        </div>
        <static-ip-adding-panel
            v-if="isIpAddingPanelShow"
            :allow-unfold-input="allowUnfoldInput"
            :static-ips="staticIps"
            :type="addingType"
            :static-ip-table-config="staticIpTableConfig"
            @onTableConfigChange="onTableConfigChange"
            @onAddIpConfirm="onAddIpConfirm"
            @onAddIpCancel="onAddIpCancel">
        </static-ip-adding-panel>
    </div>
</template>
<script>
    import '@/utils/i18n.js' // ip选择器兼容标准运维国际化

    import StaticIpAddingPanel from './StaticIpAddingPanel.vue'
    import IpSearchInput from './IpSearchInput.vue'
    import IpSelectorTable from './IpSelectorTable.vue'
    import tools from '@/utils/tools.js'

    export default {
        name: 'StaticIp',
        components: {
            StaticIpAddingPanel,
            IpSearchInput,
            IpSelectorTable
        },
        props: {
            allowUnfoldInput: Boolean,
            editable: Boolean,
            staticIpTableConfig: Array,
            staticIps: Array
        },
        data () {
            return {
                isDropdownShow: false,
                isIpAddingPanelShow: false,
                addingType: '',
                isSearchMode: false,
                copyText: '',
                pagination: {
                    limit: 5,
                    count: 0,
                    current: 1
                },
                keyword: '',
                isRemoved: false,
                staticIpList: [],
                searchResult: [],
                dataError: false,
                operations: [
                    {
                        type: 'copyIp',
                        name: this.$t('复制所有IP')
                    },
                    {
                        type: 'copyAgentIp',
                        name: this.$t('复制异常IP')
                    },
                    {
                        type: 'clearIp',
                        name: this.$t('清除所有IP')
                    },
                    {
                        type: 'clearFailedAgentIp',
                        name: this.$t('清除异常IP')
                    }
                ],
                isUnfold: false
            }
        },
        computed: {
            abnormalLength () {
                return this.staticIps.filter(item => item.agent !== 1 || item.diff).length
            }
        },
        watch: {
            staticIps: {
                handler () {
                    if (this.isRemoved) {
                        this.isRemoved = false
                        this.searchResult = this.getSearchResult()
                        this.updateStaticIpList({ list: this.searchResult, current: this.pagination.current })
                    } else {
                        this.updateStaticIpList()
                    }
                    this.dataError = this.staticIps.length === 0
                },
                deep: true,
                immediate: true
            }
        },
        methods: {
            updateStaticIpList ({ list = this.staticIps, current = 1 } = {}) {
                this.pagination.current = current
                this.pagination.count = list.length
                const offset = current === 1 ? 0 : ((current - 1) * this.pagination.limit)
                this.staticIpList = list.slice(offset, current * this.pagination.limit)
            },
            onAddPanelShow (type) {
                if (!this.editable) {
                    return
                }
                this.addingType = type
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
                const ipStr = this.staticIps.filter(item => item.agent !== 1 || item.diff).map(d => d.bk_host_innerip).join(',')
                this.handleIpCopy(ipStr)
            },
            clearIp () {
                this.$emit('change', [])
            },
            clearFailedAgentIp () {
                const staticIps = this.staticIps.filter(item => item.agent === 1 && !item.diff)
                this.$emit('change', staticIps)
            },
            onDropdownShow () {
                this.isDropdownShow = true
            },
            onDropdownHide () {
                this.isDropdownShow = false
            },
            onStaticIpFocus () {
                this.isUnfold = this.allowUnfoldInput
            },
            getSearchResult (keyword = this.keyword) {
                const ipv6Regexp = tools.getIpv6Regexp()
                const keyArr = keyword.split(',').map(item => item.trim()).filter(Boolean)

                if (!keyword) return this.staticIps

                return this.staticIps.filter(item => {
                    const { bk_host_innerip: ipv4, bk_host_innerip_v6: ipv6 } = item
                    return keyArr.some(str => {
                        const text = ipv6Regexp.test(str) ? tools.tranSimIpv6ToFullIpv6(str) : str
                        return ipv4.includes(text) || (ipv6 && ipv6.includes(text))
                    })
                })
            },
            onStaticIpSearch (keyword) {
                this.keyword = keyword
                const list = this.getSearchResult()

                this.searchResult = list
                this.updateStaticIpList({ list })
                this.isSearchMode = Boolean(keyword)
            },
            onOperationClick (operation) {
                const { type, name } = operation
                this[type] && this[type]()
                this.$bkMessage({
                    message: name + this.$t('成功'),
                    theme: 'success'
                })
            },
            onTableConfigChange (data) {
                this.$emit('onTableConfigChange', data)
            },
            onRemoveIpClick (id) {
                if (!this.editable) return
                const index = this.staticIps.findIndex(item => item.bk_host_id === id)
                if (index === -1) return

                const updatedIps = [...this.staticIps]
                updatedIps.splice(index, 1)
                // 如果当前删除的ip是本页最后一条数据，则页数-1
                if (this.staticIpList.length === 1 && this.pagination.current > 1) {
                    this.pagination.current -= 1
                }
                this.isRemoved = true
                this.$emit('change', updatedIps)
            },
            onAddIpConfirm (data) {
                this.$emit('change', data)
                this.isIpAddingPanelShow = false
            },
            onAddIpCancel () {
                this.isIpAddingPanelShow = false
            },
            onPageChange (page) {
                const list = this.searchResult.length ? this.searchResult : this.staticIps
                this.updateStaticIpList({ list, current: page })
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
    .bk-button {
        font-size: 12px;
    }
    .bk-dropdown-menu {
        margin-left: 4px;
    }
    .trigger-btn {
        width: 162px;
        padding: 0px;
        font-size: 12px;
    }
    &.is-view {
        > .bk-dropdown-menu,
        > .bk-button {
            transform: scale(0);
        }
    }
}
.operation-btn {
    padding: 5px 8px;
    font-size: 12px;
    cursor: pointer;
    &:hover {
        color: #3a84ff;
        background: #ebf4ff;
    }
}
.ip-search-wrap {
    position: absolute;
    top: 0px;
    right: 0;
    width: 32%;
    &.static-ip-unfold {
        left: 0;
        width: 356px;
    }
}
.return-text {
    position: absolute;
    left: 368px;
    top: 5px;
    color: #3a84ff;
    cursor: pointer;
}
.table-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    transform: translateY(10px);
    .selected-num {
        font-size: 12px;
        .total-ip {
            color: #3a84ff;
        }
        .total-not-installed {
            color: #ea3636;
        }
    }
}
</style>
