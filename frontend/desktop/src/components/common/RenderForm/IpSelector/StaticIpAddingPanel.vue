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
    <div class="static-ip-adding-panel">
        <ip-search-input
            v-if="type === 'select'"
            :class="['ip-search-wrap', { 'static-ip-unfold': allowUnfoldInput }]"
            @search="onIpSearch">
        </ip-search-input>
        <div class="ip-list-wrap">
            <template v-if="type === 'select'">
                <IpSelectorTable
                    :selection="true"
                    :editable="true"
                    :operate="false"
                    :is-search-mode="isSearchMode"
                    :default-selected="selectedIp"
                    :static-ip-list="staticIpList"
                    :list-in-page="listInPage"
                    :static-ip-table-config="staticIpTableConfig"
                    @onIpSort="onIpSort"
                    @onHostNameSort="onHostNameSort"
                    @onTableConfigChange="onTableConfigChange"
                    @handleSelectionChange="handleSelectionChange">
                </IpSelectorTable>
                
                <bk-pagination
                    v-if="isPaginationShow"
                    class="table-pagination"
                    size="small"
                    align="right"
                    :current="currentPage"
                    :count="totalCount"
                    :limit="listCountPerPage"
                    :limit-list="[listCountPerPage]"
                    :show-limit="false"
                    @change="onPageChange">
                </bk-pagination>
            </template>
            <template v-else>
                <div class="manual-input">
                    <bk-input
                        type="textarea"
                        :rows="10"
                        :placeholder="$t('请输入IP，多个以逗号或者换行符隔开')"
                        v-model="ipString">
                    </bk-input>
                </div>
            </template>
        </div>
        <div id="error-ips-content">
            <div v-for="(item, index) in errorIpList" :key="index" class="error-ip">{{ item }}</div>
        </div>
        <div class="adding-footer">
            <div class="ip-list-btns">
                <bk-button theme="primary" size="small" @click.stop="onAddIpConfirm">{{$t('添加')}}</bk-button>
                <bk-button theme="default" size="small" @click.stop="onAddIpCancel">{{$t('取消')}}</bk-button>
            </div>
            <div class="message-wrap">
                <span v-if="type === 'select'">{{$t('已选择')}} {{selectedIp.length}} {{$t('个')}}</span>
                <span v-if="type === 'manual' && errorIpList.length > 0">
                    <span style="color: red;">{{ errorIpList.length }}</span>{{ errorStr }}
                    <span class="view-error-ip-btn" v-bk-tooltips="tooltipConfig">{{ $t('查看详情') }}</span>
                </span>
            </div>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js' // ip选择器兼容标准运维国际化

    import IpSearchInput from './IpSearchInput.vue'
    import IpSelectorTable from './IpSelectorTable.vue'
    import tools from '@/utils/tools.js'

    export default {
        name: 'StaticIpAddingPanel',
        components: {
            IpSearchInput,
            IpSelectorTable
        },
        props: {
            allowUnfoldInput: Boolean,
            staticIpList: Array,
            staticIpTableConfig: Array,
            staticIps: Array,
            type: String
        },
        data () {
            const listCountPerPage = 5
            const listInPage = this.staticIpList.slice(0, listCountPerPage)
            const totalPage = Math.ceil(this.staticIpList.length / listCountPerPage)

            return {
                isPaginationShow: totalPage > 1,
                selectedIp: this.staticIps.slice(0),
                isSearchMode: false,
                searchResult: [],
                currentPage: 1,
                totalCount: this.staticIpList.length,
                listCountPerPage,
                listInPage,
                ipSortActive: '',
                hostNameSortActive: '',
                ipString: '',
                list: this.staticIpList, // 筛选/排序后存放列表
                errorStr: '',
                errorIpList: [],
                tooltipConfig: {
                    allowHtml: true,
                    width: 300,
                    theme: 'light',
                    content: '#error-ips-content',
                    placement: 'top'
                },
                isSearchInputFocus: false
            }
        },
        watch: {
            staticIpList (val) {
                this.setDisplayList()
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
                let list = this.isSearchMode ? this.searchResult : this.staticIpList
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
            onIpSearch (keyword) {
                if (keyword) {
                    const keyArr = keyword.split(',').map(item => item.trim()).filter(item => {
                        return item.trim() !== ''
                    })
                    const ipv6Regexp = tools.getIpv6Regexp()
                    const list = this.staticIpList.filter(item => {
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
                    this.setPanigation(this.staticIpList)
                    this.isSearchMode = false
                }
            },
            handleSelectionChange (ips) {
                this.selectedIp = ips
            },
            onTableConfigChange (data) {
                this.$emit('onTableConfigChange', data)
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
            },
            onPageChange (page) {
                const list = this.isSearchMode ? this.searchResult : this.list
                this.currentPage = page
                this.listInPage = list.slice((page - 1) * this.listCountPerPage, page * this.listCountPerPage)
            },
            onAddIpConfirm () {
                const selectedIp = this.selectedIp.slice(0)

                if (this.type === 'manual') {
                    const ipInvalidList = []
                    const ipNotExistList = []
                    const ipPattern = /^((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}$/ // ip 地址正则规则
                    const ipv6Regexp = tools.getIpv6Regexp() // ipv6 地址正则规则
                    const arr = this.ipString.split(/[\,|\n|\uff0c]/) // 按照中英文逗号、换行符分割
                    arr.forEach(item => {
                        const str = item.trim()
                        if (str) {
                            if (!ipPattern.test(str) && !ipv6Regexp.test(str)) { // 字符串不是合法 ip 地址
                                ipInvalidList.push(str)
                            } else {
                                let text = str
                                if (ipv6Regexp.test(str)) { // 判断是否为ipv6地址
                                    text = tools.tranSimIpv6ToFullIpv6(str) // 将缩写的ipv6转换为全写
                                }
                                const ipInList = this.list.find(i => [i.bk_host_innerip, i.bk_host_innerip_v6].includes(text))
                                if (!ipInList) { // ip 地址/ipv6地址不在可选列表里
                                    ipNotExistList.push(str)
                                } else {
                                    const ipInSelected = this.selectedIp.find(i => [i.bk_host_innerip, i.bk_host_innerip_v6].includes(text))
                                    if (!ipInSelected) { // ip 地址/ipv6地址在可选列表并且不在已选列表
                                        selectedIp.push(ipInList)
                                    }
                                }
                            }
                        }
                    })
                    if (ipInvalidList.length > 0) {
                        this.errorStr = ` ${this.$t('个')} ${this.$t('IP地址不合法，')}`
                        this.errorIpList = ipInvalidList
                        return
                    }
                    if (ipNotExistList.length > 0) {
                        this.errorStr = ` ${this.$t('个')} ${this.$t('IP地址不存在，')}`
                        this.errorIpList = ipNotExistList
                        return
                    }
                }

                this.$emit('onAddIpConfirm', selectedIp)
            },
            onAddIpCancel () {
                this.$emit('onAddIpCancel')
            }
        }
    }
</script>
<style lang="scss" scoped>
.static-ip-adding-panel {
    position: relative;
}
.ip-search-wrap {
    width: 32%;
    margin: 20px 0;
    &.static-ip-unfold {
        width: 356px;
    }
}
.ip-list-wrap {
    position: relative;
    .table-pagination {
        position: absolute;
        right: 0;
        bottom: -42px;
        z-index: 1;
    }
}
.adding-footer {
    position: relative;
    margin: 13px 0;
    .message-wrap {
        position: absolute;
        top: 8px;
        left: 160px;
        line-height: 1;
        font-size: 12px;
        color: #313238;
    }
    .view-error-ip-btn {
        color: #3a84ff;
        cursor: pointer;
    }
}
</style>
<style lang="scss">
    #error-ips-content {
        max-height: 260px;
        word-break: break-all;
        overflow-y: auto;
    }
</style>
