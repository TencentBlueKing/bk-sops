/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <bk-dialog
        width="600"
        :ext-cls="'common-dialog'"
        :theme="'primary'"
        :mask-close="false"
        :header-position="'left'"
        :title="$t('启动记录')"
        :value="show"
        data-test-id="periodicList_form_bootRecordDialog"
        @cancel="onCloseDialog">
        <div class="dialog-content" v-bkloading="{ isLoading: loading, opacity: 1, zIndex: 100 }">
            <bk-table :data="recordData" :max-height="350" ref="recordTable">
                <bk-table-column type="expand" width="30" align="center">
                    <template slot-scope="props">
                        <div v-if="props.row.ex_data" v-html="transformFailInfo(props.row.ex_data)"></div>
                        <div class="no-error" v-else>{{ $t('无异常信息') }}</div>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t('序号')" prop="id"></bk-table-column>
                <bk-table-column :width="200" :label="$t('启动时间')" prop="start_at"></bk-table-column>
                <bk-table-column :label="$t('是否启动成功')">
                    <template slot-scope="props">
                        {{ props.row.start_success ? $t('是') : $t('否') }}
                    </template>
                </bk-table-column>
                <bk-table-column :width="80" :label="$t('异常信息')">
                    <template slot-scope="props">
                        <span
                            v-if="!props.row.start_success"
                            class="view-btn"
                            @click="$refs.recordTable.toggleRowExpansion(props.row)">
                            {{ $t('查看') }}
                        </span>
                        <span v-else>--</span>
                    </template>
                </bk-table-column>
                <div class="no-data-matched" slot="empty"><NoData /></div>
                <div class="is-loading" slot="append" v-if="isLoading" v-bkloading="{ isLoading: isLoading, zIndex: 100 }"></div>
            </bk-table>
        </div>
        <div class="footer-wrapper" slot="footer">
            <bk-button @click="onCloseDialog">{{ $t('关闭') }}</bk-button>
        </div>
    </bk-dialog>
</template>
<script>
    import { mapActions } from 'vuex'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'BootRecordDialog',
        components: {
            NoData
        },
        props: {
            show: {
                type: Boolean,
                default: false
            },
            id: {
                type: Number,
                default: null
            }
        },
        data () {
            return {
                isLoading: false, // 加载loading
                isThrottled: false, // 滚动节流 是否进入cd
                isPageOver: false, // 前端分页加载是否结束
                pageSize: 15, // 每页展示多少数据
                totalPage: null, // 计算出总共多少页
                currentPage: 0, // 当前加载了多少页
                pollingTimer: null,
                loading: true,
                isShow: this.show,
                recordData: []
            }
        },
        watch: {
            show (val) {
                if (val) {
                    this.isShow = val
                    this.currentPage = 0
                    this.offset = 0
                    this.recordData = []
                    this.getRecord()
                }
            }
        },
        mounted () {
            this.tableScroller = this.$el.querySelector('.bk-table-body-wrapper')
            this.tableScroller.addEventListener('scroll', this.handleTableScroll, { passive: true })
        },
        beforeDestroy () {
            this.tableScroller.removeEventListener('scroll', this.handleTableScroll)
        },
        methods: {
            ...mapActions('admin/', [
                'periodTaskHistory'
            ]),
            handleTableScroll () {
                if (!this.isPageOver && !this.isThrottled) {
                    this.isThrottled = true
                    this.pollingTimer = setTimeout(() => {
                        this.isThrottled = false
                        const el = this.tableScroller
                        if (el.scrollHeight - el.offsetHeight - el.scrollTop < 10) {
                            this.currentPage += 1
                            this.isPageOver = this.currentPage === this.totalPage
                            clearTimeout(this.pollingTimer)
                            this.isLoading = true
                            this.getRecord()
                        }
                    }, 200)
                }
            },
            async getRecord () {
                try {
                    if (!this.currentPage) {
                        this.loading = true
                    }
                    const resp = await this.periodTaskHistory({
                        task_id: this.id,
                        limit: this.pageSize,
                        offset: this.currentPage * this.pageSize
                    })
                    this.totalPage = Math.floor(resp.count / this.pageSize)
                    this.recordData.push(...resp.results)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.isLoading = false
                    this.loading = false
                }
            },
            transformFailInfo (data) {
                if (!data) {
                    return ''
                }
                if (typeof data === 'string') {
                    const info = data.replace(/\n/g, '<br>')
                    return info
                } else {
                    return data
                }
            },
            onCloseDialog () {
                this.$emit('onClose')
            }
        }
    }
</script>

<style lang="scss" scoped>
    .dialog-content {
        padding: 30px;
    }
    .information-tips {
        word-break: break-all;
    }
    .no-error {
        text-align: center;
    }
    .view-btn {
        color: #3a84ff;
        cursor: pointer;
    }
    .is-loading {
        height: 42px;
    }
</style>
