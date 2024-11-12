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
        <div class="ip-list-wrap" v-bkloading="{ isLoading: isLoading }">
            <template v-if="type === 'select'">
                <IpSelectorTable
                    :selection="true"
                    :editable="true"
                    :operate="false"
                    :is-search-mode="isSearchMode"
                    :default-selected="selectedIp"
                    :static-ip-list="staticIpList"
                    :list-count="pagination.count"
                    :static-ip-table-config="staticIpTableConfig"
                    @onSelectAllClick="onSelectAllClick"
                    @onHostItemClick="onHostItemClick"
                    @onTableConfigChange="onTableConfigChange">
                </IpSelectorTable>
                <bk-pagination
                    v-if="isPaginationShow"
                    class="table-pagination"
                    size="small"
                    align="right"
                    v-bind="pagination"
                    :limit-list="[pagination.limit]"
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
                        :value="ipString"
                        @change="onManualInputChange">
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
    import { mapActions } from 'vuex'

    export default {
        name: 'StaticIpAddingPanel',
        components: {
            IpSearchInput,
            IpSelectorTable
        },
        props: {
            allowUnfoldInput: Boolean,
            staticIpTableConfig: Array,
            staticIps: Array,
            type: String
        },
        inject: ['remoteUrl'],
        data () {
            return {
                selectedIp: this.staticIps.slice(0),
                isSearchMode: false,
                staticIpList: [],
                hostNameSortActive: '',
                ipString: '',
                errorStr: '',
                errorIpList: [],
                tooltipConfig: {
                    allowHtml: true,
                    width: 300,
                    theme: 'light',
                    content: '#error-ips-content',
                    placement: 'top'
                },
                isSearchInputFocus: false,
                isLoading: false,
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 5
                }
            }
        },
        computed: {
            isPaginationShow () {
                const { count, limit } = this.pagination
                const totalPage = Math.ceil(count / limit)
                return totalPage > 1
            },
            urls () {
                return typeof this.remoteUrl === 'function' ? this.remoteUrl() : Object.assign({}, this.remoteUrl)
            }
        },
        created () {
            this.getStaticIpList()
        },
        methods: {
            ...mapActions([
                'getHostInCC'
            ]),
            async getStaticIpList () {
                try {
                    if (!this.urls['cc_search_host']) return

                    this.isLoading = true
                    const { limit, current } = this.pagination
                    const resp = await this.getHostInCC({
                        url: this.urls['cc_search_host'],
                        fields: ['agent', 'bk_host_innerip_v6'],
                        start: (current - 1) * limit,
                        limit,
                        ip_str: this.ipString || undefined
                    })
                    const { result, data } = resp
                    if (!result) return
                    // 如果传了分页返回的数据结构会多包一层
                    this.staticIpList = data.data
                    this.pagination.count = data.count
                } catch (error) {
                    console.error(error)
                } finally {
                    this.isLoading = false
                }
            },
            onIpSearch (keyword) {
                this.ipString = keyword
                this.pagination.current = 1
                this.getStaticIpList()
            },
            onTableConfigChange (data) {
                this.$emit('onTableConfigChange', data)
            },
            onPageChange (page) {
                this.pagination.current = page
                this.getStaticIpList()
            },
            // 全选
            async onSelectAllClick (val) {
                if (!val) {
                    this.selectedIp = []
                } else {
                    const resp = await this.getHostInCC({
                        url: this.urls['cc_search_host'],
                        fields: ['agent', 'bk_host_innerip_v6'],
                        ip_str: this.ipString || undefined
                    })
                    this.selectedIp = [...resp.data]
                }
            },
            // 单选
            onHostItemClick (host) {
                const index = this.selectedIp.findIndex(el => el.bk_host_id === host.bk_host_id)
                if (index > -1) {
                    this.selectedIp.splice(index, 1)
                } else {
                    this.selectedIp.push(host)
                }
            },
            onManualInputChange (val) {
                const ipString = val.split(/[\,|\n|\uff0c]/) // 按照中英文逗号、换行符分割
                this.ipString = ipString.join(',')
            },
            async onAddIpConfirm () {
                const selectedIp = this.selectedIp.slice(0)

                if (this.type === 'manual') {
                    const ipPattern = /^((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}$/ // ip 地址正则规则
                    const ipv6Regexp = tools.getIpv6Regexp() // ipv6 地址正则规则
                    const strArr = this.ipString.split(',')

                    // 校验是否为合法 ip 地址
                    const ipInvalidList = strArr.filter(str => !ipPattern.test(str) && !ipv6Regexp.test(str))
                    if (ipInvalidList.length > 0) {
                        this.errorStr = ` ${this.$t('个')} ${this.$t('IP地址不合法，')}`
                        this.errorIpList = ipInvalidList
                        return
                    }

                    // 检查ip是否存在
                    if (!this.urls['cc_search_host']) return
                    try {
                        const resp = await this.getHostInCC({
                            url: this.urls['cc_search_host'],
                            fields: ['agent', 'bk_host_innerip_v6'],
                            ip_str: this.ipString || undefined
                        })
                        const ipNotExistList = strArr.filter(str => !resp.data.find(i => [i.bk_host_innerip, i.bk_host_innerip_v6].includes(str)))
                        if (ipNotExistList.length > 0) {
                            this.errorStr = ` ${this.$t('个')} ${this.$t('IP地址不存在，')}`
                            this.errorIpList = ipNotExistList
                            return
                        }

                        // 判断输入的ip是否已经选中
                        strArr.forEach(str => {
                            const ipInSelected = this.selectedIp.find(i => [i.bk_host_innerip, i.bk_host_innerip_v6].includes(str))
                            if (!ipInSelected) { // ip 地址/ipv6地址在可选列表并且不在已选列表
                                const ipInfo = resp.data.find(i => [i.bk_host_innerip, i.bk_host_innerip_v6].includes(str))
                                selectedIp.push(ipInfo)
                            }
                        })
                    } catch (error) {
                        console.error(error)
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
