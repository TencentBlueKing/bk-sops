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
                </template>
                <span v-if="isUnfold" @click="isUnfold = false" class="return-text">{{ i18n.return }}</span>
            </div>
            <div class="selected-ip-table-wrap">
                <IpSelectorTable
                    :editable="editable"
                    :is-search-mode="isSearchMode"
                    :list-in-page="listInPage"
                    :static-ip-table-config="staticIpTableConfig"
                    @onIpSort="onIpSort"
                    @onHostNameSort="onHostNameSort"
                    @onAddPanelShow="onAddPanelShow"
                    @onTableConfigChange="onTableConfigChange"
                    @onRemoveIpClick="onRemoveIpClick">
                </IpSelectorTable>
                <div class="table-footer" v-if="isShowQuantity || isPaginationShow">
                    <div v-if="isShowQuantity" class="selected-num">{{$t('共')}}
                        <span class="total-ip">{{staticIps.length}}</span>
                        {{$t('个静态IP，')}}
                        {{$t('其中')}}
                        <span class="total-not-installed">{{failedAgentLength}}</span>
                        {{$t('个')}}{{$t('异常')}}
                    </div>
                    <div class="table-pagination" v-if="isPaginationShow">
                        <bk-pagination
                            size="small"
                            align="right"
                            :current="currentPage"
                            :count="totalCount"
                            :limit="listCountPerPage"
                            :limit-list="[listCountPerPage]"
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
            :static-ip-list="staticIpList"
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
            staticIpList: Array,
            staticIpTableConfig: Array,
            staticIps: Array
        },
        data () {
            const listCountPerPage = 5
            const totalPage = Math.ceil(this.staticIps.length / listCountPerPage)
            return {
                isDropdownShow: false,
                isIpAddingPanelShow: false,
                addingType: '',
                isSearchMode: false,
                copyText: '',
                ipSortActive: '', // ip 排序方式
                hostNameSortActive: '', // hostname 排序方式
                searchResult: [],
                list: this.staticIps,
                isPaginationShow: totalPage > 1,
                currentPage: 1,
                totalCount: this.staticIps.length,
                listCountPerPage: listCountPerPage,
                listInPage: this.staticIps.slice(0, listCountPerPage),
                dataError: false,
                operations: [
                    {
                        type: 'copyIp',
                        name: this.$t('复制IP')
                    },
                    {
                        type: 'copyAgentIp',
                        name: this.$t('复制Agent异常IP')
                    },
                    {
                        type: 'clearIp',
                        name: this.$t('清空IP')
                    },
                    {
                        type: 'clearFailedAgentIp',
                        name: this.$t('清空Agent异常IP')
                    }
                ],
                isUnfold: false
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
                this.setDisplayList()
                if (this.staticIps.length !== 0) {
                    this.dataError = false
                }
            },
            isSearchMode () {
                this.setDisplayList()
            },
            ipSortActive () {
                this.setDisplayList()
            },
            hostNameSortActive () {
                this.setDisplayList()
            }
        },
        methods: {
            setDisplayList () {
                let list = this.isSearchMode ? this.searchResult : this.staticIps
                if (this.ipSortActive) {
                    list = this.getSortIpList(list, this.ipSortActive)
                }
                if (this.hostNameSortActive) {
                    list = this.getSortHostNameList(list, this.hostNameSortActive)
                }
                this.list = list
                this.setPanigation(list)
            },
            setPanigation (list = []) {
                this.listInPage = list.slice(0, this.listCountPerPage)
                const totalPage = Math.ceil(list.length / this.listCountPerPage)
                this.isPaginationShow = totalPage > 1
                this.totalCount = list.length
                this.currentPage = 1
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
            onStaticIpFocus () {
                this.isUnfold = this.allowUnfoldInput
            },
            onStaticIpSearch (keyword) {
                if (keyword) {
                    const keyArr = keyword.split(',').map(item => item.trim()).filter(item => {
                        return item !== ''
                    })
                    const ipv6Regexp = tools.getIpv6Regexp()
                    const list = this.staticIps.filter(item => {
                        const { bk_host_innerip: ipv4, bk_host_innerip_v6: ipv6 } = item
                        return keyArr.some(str => {
                            let text = str
                            if (ipv6Regexp.test(str)) { // 判断是否为ipv6地址
                                text = tools.tranSimIpv6ToFullIpv6(str) // 将缩写的ipv6转换为全写
                            }
                            return ipv4.indexOf(text) > -1
                                || (ipv6 && ipv6.indexOf(text) > -1)
                        })
                    })
                    this.searchResult = list
                    this.setPanigation(list)
                    this.isSearchMode = true
                } else {
                    this.setPanigation(this.staticIps)
                    this.isSearchMode = false
                }
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
                if (!this.editable) {
                    return
                }
                const index = this.staticIps.findIndex(item => item.bk_host_id === id)
                const staticIps = this.staticIps.slice(0)
                staticIps.splice(index, 1)
                if (this.isSearchMode) { // 搜索模式下移除 ip
                    this.searchResult = []
                    this.setDisplayList()
                }
                this.$emit('change', staticIps)
            },
            onAddIpConfirm (data) {
                this.$emit('change', data)
                this.isIpAddingPanelShow = false
                this.$nextTick(() => {
                    this.$refs.ipSearchInput.handleSearch()
                })
            },
            onAddIpCancel () {
                this.isIpAddingPanelShow = false
            },
            onPageChange (page) {
                this.currentPage = page
                this.listInPage = this.list.slice((page - 1) * this.listCountPerPage, page * this.listCountPerPage)
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
            },
            getSortIpList (list, way = 'up') {
                const srotList = list.slice(0)
                const sortVal = way === 'up' ? 1 : -1
                srotList.sort((a, b) => {
                    const srotA = a.bk_host_innerip.split('.')
                    const srotB = b.bk_host_innerip.split('.')
                    for (let i = 0; i < 4; i++) {
                        if (srotA[i] * 1 > srotB[i] * 1) {
                            return sortVal
                        } else if (srotA[i] * 1 < srotB[i] * 1) {
                            return -sortVal
                        }
                    }
                })
                return srotList
            },
            getSortHostNameList (list, way = 'up') {
                const sortList = list.slice(0)
                const sortVal = way === 'up' ? 1 : -1
                sortList.sort((a, b) => {
                    if (a.bk_host_name > b.bk_host_name) {
                        return sortVal
                    } else {
                        return -sortVal
                    }
                })
                return sortList
            },
            onIpSort (way) {
                this.hostNameSortActive = ''
                this.ipSortActive = way
            },
            onHostNameSort (way) {
                this.ipSortActive = ''
                this.hostNameSortActive = way
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
    margin-top: 10px;
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
