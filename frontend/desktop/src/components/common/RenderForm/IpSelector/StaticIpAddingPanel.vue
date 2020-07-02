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
    <div class="static-ip-adding-panel">
        <ip-search-input
            v-if="type === 'select'"
            class="ip-search-wrap"
            @search="onIpSearch">
        </ip-search-input>
        <div class="ip-list-wrap">
            <template v-if="type === 'select'">
                <table class="ip-table">
                    <thead>
                        <tr>
                            <th width="40">
                                <span
                                    :class="['checkbox', {
                                        'checked': listAllSelected === true,
                                        'half-checked': listAllSelected === 'half'
                                    }]"
                                    @click="onSelectAllClick">
                                </span>
                            </th>
                            <th>{{i18n.cloudArea}}</th>
                            <th width="120">
                                IP
                                <span class="sort-group">
                                    <i :class="['sort-icon', 'up', { 'active': ipSortActive === 'up' }]" @click="onIpSort('up')"></i>
                                    <i :class="['sort-icon', { 'active': ipSortActive === 'down' }]" @click="onIpSort('down')"></i>
                                </span>
                            </th>
                            <th width="160">Agent {{i18n.status}}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-if="listInPage.length">
                            <tr v-for="item in listInPage" :key="item.bk_host_id">
                                <td>
                                    <span
                                        :class="['checkbox', { 'checked': selectedIp.findIndex(el => el.bk_host_id === item.bk_host_id) > -1 }]"
                                        @click="onHostItemClick(item)">
                                    </span>
                                </td>
                                <td
                                    class="ui-ellipsis"
                                    :title="item.cloud[0] && item.cloud[0].bk_inst_name">
                                    {{ item.cloud[0] && item.cloud[0].bk_inst_name }}
                                </td>
                                <td>{{item.bk_host_innerip}}</td>
                                <td
                                    class="ui-ellipsis"
                                    :class="item.agent ? 'agent-normal' : 'agent-failed'"
                                    :title="item.agent ? 'Agent' + i18n.normal : 'Agent' + i18n.error">
                                    {{item.agent ? 'Agent' + i18n.normal : 'Agent' + i18n.error}}
                                </td>
                            </tr>
                        </template>
                        <tr v-else>
                            <td class="static-ip-empty" colspan="4">{{i18n.noData}}</td>
                        </tr>
                    </tbody>
                </table>
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
                        :placeholder="i18n.manualPlaceholder"
                        v-model="ipString">
                    </bk-input>
                </div>
            </template>
        </div>
        <div class="error-ips-content" v-if="isErrorIpsShow">
            <div v-for="(item, index) in errorIpList" :key="index" class="error-ip">{{ item }}</div>
        </div>
        <div class="adding-footer">
            <div class="ip-list-btns">
                <bk-button theme="primary" @click.stop="onAddIpConfirm">{{i18n.add}}</bk-button>
                <bk-button theme="default" @click.stop="onAddIpCancel">{{i18n.cancel}}</bk-button>
            </div>
            <div class="message-wrap">
                <span v-if="type === 'select'">{{i18n.selected}} {{selectedIp.length}} {{i18n.number}}</span>
                <span v-if="type === 'manual' && errorIpList.length > 0">
                    <span style="color: red;">{{ errorIpList.length }}</span>{{ errorStr }}
                    <span v-if="isErrorIpsShow" class="hide-error-ip-btn" @click="isErrorIpsShow = false">{{ i18n.hideDetail }}<i class="common-icon-double-arrow"></i></span>
                    <span v-else class="view-error-ip-btn" @click="isErrorIpsShow = true">{{ i18n.viewDetail }}<i class="common-icon-double-arrow"></i></span>
                </span>
            </div>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js' // ip选择器兼容标准运维国际化

    import IpSearchInput from './IpSearchInput.vue'

    const i18n = {
        add: gettext('添加'),
        selected: gettext('已选择'),
        number: gettext('个'),
        cloudArea: gettext('云区域'),
        status: gettext('状态'),
        error: gettext('异常'),
        noData: gettext('无数据'),
        normal: gettext('正常'),
        cancel: gettext('取消'),
        manualPlaceholder: gettext('请输入IP，多个以逗号隔开'),
        ipInvalid: gettext('IP地址不合法，'),
        ipNotExist: gettext('IP地址不存在，'),
        viewDetail: gettext('查看详情'),
        hideDetail: gettext('隐藏详情')
    }

    export default {
        name: 'StaticIpAddingPanel',
        components: {
            IpSearchInput
        },
        props: {
            staticIpList: Array,
            staticIps: Array,
            type: String
        },
        data () {
            const listCountPerPage = 5
            const listInPage = this.staticIpList.slice(0, listCountPerPage)
            const totalPage = Math.ceil(this.staticIpList.length / listCountPerPage)

            return {
                listAllSelected: false,
                isPaginationShow: totalPage > 1,
                selectedIp: this.staticIps.slice(0),
                isSearchMode: false,
                searchResult: [],
                currentPage: 1,
                totalCount: this.staticIpList.length,
                listCountPerPage,
                listInPage,
                ipSortActive: '',
                ipString: '',
                list: this.staticIpList,
                errorStr: '',
                errorIpList: [],
                isErrorIpsShow: false,
                i18n
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
            }
        },
        methods: {
            setDisplayList () {
                let list = this.isSearchMode ? this.searchResult : this.staticIpList
                if (this.ipSortActive) {
                    list = this.getSortIpList(list, this.ipSortActive)
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
                    const list = this.staticIpList.filter(item => {
                        return keyArr.some(str => item.bk_host_innerip.indexOf(str) > -1)
                    })
                    this.searchResult = list
                    this.setPanigation(list)
                    this.isSearchMode = true
                } else {
                    this.setPanigation(this.staticIpList)
                    this.isSearchMode = false
                }
            },
            onSelectAllClick () {
                if (this.listAllSelected) {
                    this.listInPage.forEach(item => {
                        const index = this.selectedIp.findIndex(el => el.bk_host_id === item.bk_host_id)
                        this.selectedIp.splice(index, 1)
                    })
                    this.listAllSelected = false
                } else {
                    this.listInPage.forEach(item => {
                        const index = this.selectedIp.findIndex(el => el.bk_host_id === item.bk_host_id)
                        if (index === -1) {
                            this.selectedIp.push(item)
                        }
                    })
                    this.listAllSelected = true
                }
            },
            onHostItemClick (host) {
                const index = this.selectedIp.findIndex(el => el.bk_host_id === host.bk_host_id)
                let checkedNumInPage = 0
            
                this.listInPage.forEach(el => {
                    if (this.selectedIp.findIndex(item => item.bk_host_id === el.bk_host_id) > -1) {
                        checkedNumInPage += 1
                    }
                })
                if (index > -1) {
                    this.selectedIp.splice(index, 1)
                    this.listAllSelected = checkedNumInPage > 1 ? 'half' : false
                } else {
                    this.selectedIp.push(host)
                    this.listAllSelected = checkedNumInPage === this.listInPage.length - 1 ? true : 'half'
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
            onIpSort (way) {
                if (this.ipSortActive === way) {
                    this.ipSortActive = ''
                    return
                }
                this.ipSortActive = way
            },
            onPageChange (page) {
                this.currentPage = page
                this.listAllSelected = false
                this.listInPage = this.list.slice((page - 1) * this.listCountPerPage, page * this.listCountPerPage)
            },
            onAddIpConfirm () {
                const selectedIp = this.selectedIp.slice(0)

                if (this.type === 'manual') {
                    const ipInvalidList = []
                    const ipNotExistList = []
                    const ipPattern = /^((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}$/ // ip 地址正则规则
                    const arr = this.ipString.split(/[\,|\n|\uff0c]/) // 按照中英文逗号、换行符分割
                    arr.forEach(item => {
                        const str = item.trim()
                        if (str) {
                            if (!ipPattern.test(str)) { // 字符串不是合法 ip 地址
                                ipInvalidList.push(str)
                            } else {
                                const ipInList = this.list.find(i => i.bk_host_innerip === str)
                                if (!ipInList) { // ip 地址不在可选列表里
                                    ipNotExistList.push(str)
                                } else {
                                    const ipInSelected = this.selectedIp.find(i => i.bk_host_innerip === str)
                                    if (!ipInSelected) { // ip 地址在可选列表并且不在已选列表
                                        selectedIp.push(ipInList)
                                    }
                                }
                            }
                        }
                    })
                    if (ipInvalidList.length > 0) {
                        this.errorStr = ` ${this.i18n.number} ${this.i18n.ipInvalid}`
                        this.errorIpList = ipInvalidList
                        return
                    }
                    if (ipNotExistList.length > 0) {
                        this.errorStr = ` ${this.i18n.number} ${this.i18n.ipNotExist}`
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
    position: absolute;
    top: -40px;
    right: 0;
    width: 50%;
}
.ip-list-wrap {
    position: relative;
    .ip-table {
        width: 100%;
        border: 1px solid #dde4eb;
        border-collapse: collapse;
        table-layout:fixed;
        tr {
            border-bottom: 1px solid #dde4eb;
        }
        th {
            color: #313238;
        }
        th,td {
            padding: 12px 8px;
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
        .loading-wraper {
            height: 300px;
        }
        .static-ip-empty {
            height: 300px;
            text-align: center;
            color: #c4c6cc;
            .add-ip-btn {
                color: #3a84ff;
                cursor: pointer;
            }
        }
        .checkbox {
            display: inline-block;
            position: relative;
            width: 14px;
            height: 14px;
            border: 1px solid #c4c6cc;
            border-radius: 2px;
            vertical-align: middle;
            cursor: pointer;
            &.checked {
                background: #3a84ff;
                border-color: #3a84ff;
                &:before {
                    content: '';
                    position: absolute;
                    left: 2px;
                    top: 2px;
                    height: 4px;
                    width: 8px;
                    border-left: 1px solid;
                    border-bottom: 1px solid;
                    border-color: #ffffff;
                    transform: rotate(-45deg);
                }
            }
            &.half-checked {
                background: #3a84ff;
                border-color: #3a84ff;
                &:before {
                    content: '';
                    position: absolute;
                    left: 2px;
                    top: 5px;
                    height: 1px;
                    width: 8px;
                    background: #ffffff;
                }
            }
        }
        .sort-group {
            display: inline-block;
            margin-left: 6px;
            vertical-align: top;
            .sort-icon {
                display: block;
                width: 0;
                height: 0;
                border-style: solid;
                border-width: 5px 5px 0 5px;
                border-color: #c4c6cc transparent transparent transparent;
                cursor: pointer;
                &.up {
                    margin-bottom: 2px;
                    transform: rotate(180deg);
                }
                &.active {
                    border-color: #3a84ff transparent transparent transparent;
                }
            }
        }
        .ui-ellipsis {
            overflow:hidden;
            text-overflow:ellipsis;
            white-space:nowrap;
        }
    }
    .table-pagination {
        position: absolute;
        right: 0;
        bottom: -42px;
        z-index: 1;
    }
}
.error-ips-content {
    margin: 10px 0;
    padding: 9px 13px;
    max-height: 260px;
    background: #ffffff;
    border: 1px solid #dcdee5;
    border-radius: 2px;
    box-shadow: 0 0 5px 0 rgba(0, 0, 0, 0.09);
    word-break: break-all;
    overflow-y: auto;
}
.adding-footer {
    position: relative;
    margin: 10px 0;
    .bk-button {
        font-size: 12px;
        height: 32px;
        line-height: 32px;
    }
    .message-wrap {
        position: absolute;
        top: 10px;
        left: 160px;
        line-height: 1;
        font-size: 12px;
        color: #313238;
    }
    .view-error-ip-btn,
    .hide-error-ip-btn {
        color: #3a84ff;
        cursor: pointer;
        .common-icon-double-arrow {
            display: inline-block;
            font-size: 12px;
        }
    }
    .view-error-ip-btn {
        .common-icon-double-arrow {
            margin-left: 2px;
            transform: rotate(90deg) scale(0.8);
        }
    }
    .hide-error-ip-btn {
        .common-icon-double-arrow {
            margin-left: 2px;
            transform: rotate(-90deg) scale(0.8);
        }
    }
}
</style>
