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
    <div class="static-ip-adding-panel">
        <div class="ip-added-number">{{i18n.add}}({{selectedIp.length}})</div>
        <div class="operation-area">
            <div class="ip-list-add">
                <bk-button theme="primary" @click.stop="onAddIpConfirm">{{i18n.add}}</bk-button>
                <bk-button theme="default" @click.stop="onAddIpCancel">{{i18n.cancel}}</bk-button>
            </div>
            <ip-search-input class="ip-search-wrap" @search="onIpSearch"></ip-search-input>
        </div>
        <div class="ip-list-table-wrap">
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
                        <th>IP</th>
                        <th>{{i18n.status + i18n.error}}</th>
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
                            <td>{{item.cloud[0] && item.cloud[0].bk_inst_name}}</td>
                            <td>{{item.bk_host_innerip}}</td>
                            <td :class="item.agent ? 'agent-normal' : 'agent-failed'">{{item.agent ? 'Agent' + i18n.normal : 'Agent' + i18n.error}}</td>
                        </tr>
                    </template>
                    <tr v-else>
                        <td class="static-ip-empty" colspan="4">{{i18n.noData}}</td>
                    </tr>
                </tbody>
            </table>
            <div class="table-pagination">
                <bk-pagination
                    v-if="isPaginationShow"
                    :current.sync="currentPage"
                    :count="totalCount"
                    :limit="listCountPerPage"
                    :limit-list="[15,20,30]"
                    :show-limit="false"
                    @change="onPageChange">
                </bk-pagination>
            </div>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js' // ip选择器兼容标准运维国际化

    import IpSearchInput from './IpSearchInput.vue'

    const i18n = {
        add: gettext('添加'),
        cloudArea: gettext('云区域'),
        status: gettext('状态'),
        error: gettext('异常'),
        noData: gettext('无数据'),
        normal: gettext('正常'),
        cancel: gettext('取消')
    }

    export default {
        name: 'StaticIpAddingPanel',
        components: {
            IpSearchInput
        },
        props: ['staticIpList', 'staticIps'],
        data () {
            const listCountPerPage = 5
            const listInPage = this.staticIpList.slice(0, listCountPerPage)
            const totalPage = Math.ceil(this.staticIpList.length / listCountPerPage)

            return {
                listAllSelected: false,
                isPaginationShow: totalPage > 1,
                selectedIp: this.staticIps.slice(0),
                currentPage: 1,
                totalCount: this.staticIpList.length,
                totalPage,
                listCountPerPage,
                listInPage,
                i18n
            }
        },
        watch: {
            staticIpList (val) {
                this.setPanigation(val)
            }
        },
        methods: {
            setPanigation (list = []) {
                this.listInPage = list.slice(0, this.listCountPerPage)
                this.totalPage = Math.ceil(list.length / this.listCountPerPage)
                this.isPaginationShow = this.totalPage > 1
                this.currentPage = 1
            },
            onIpSearch (keyword) {
                if (keyword) {
                    const keyArr = keyword.split(',')
                    const list = this.staticIpList.filter(item => {
                        return keyArr.some(str => item.bk_host_innerip.indexOf(str) > -1)
                    })
                    this.setPanigation(list)
                } else {
                    this.setPanigation(this.staticIpList)
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
            onPageChange (page) {
                this.currentPage = page
                this.listAllSelected = false
                this.listInPage = this.staticIpList.slice((page - 1) * this.listCountPerPage, page * this.listCountPerPage)
            },
            onAddIpConfirm () {
                this.$emit('onAddIpConfirm', this.selectedIp.slice(0))
            },
            onAddIpCancel () {
                this.$emit('onAddIpCancel')
            }
        }
    }
</script>
<style lang="scss" scoped>
.ip-added-number {
    padding: 20px 0;
    line-height: 1;
    font-size: 14px;
    color: #313238;
    border-bottom: 1px solid #dcdee5;
}
.operation-area {
    position: relative;
    .ip-list-add {
        margin: 24px 0;
    }
    .ip-search-wrap {
        position: absolute;
        top: -2px;
        right: 0;
        width: 70%;
    }
    .bk-button {
        height: 32px;
        line-height: 32px;
    }
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
