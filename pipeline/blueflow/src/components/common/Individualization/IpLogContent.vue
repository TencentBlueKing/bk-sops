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
    <div class="ip-log-content" v-bkloading="{isLoading: loading, opacity: 1}">
        <div class="detail-ip-log" v-html="logContent"></div>
        <el-input
            :placeholder="i18n.placeholder"
            v-model="search"
            class="ip-search"
            clearable>
        </el-input>
        <el-table
            border
            highlight-current-row
            class="detail-table"
            ref="singleTable"
            :data="ipList"
            @current-change="getIpLogContent">
            <el-table-column
                property="ip"
                width="140px"
                label="IP">
            </el-table-column>
            <el-table-column
                property="error_code"
                :label="i18n.error_code">
            </el-table-column>
        </el-table>
        <el-pagination
            small
            class="pagination"
            layout="prev, pager, next"
            :page-size="pageSize"
            :pager-count="pageCount"
            :total="dataTotal.length"
            @current-change="currentChange">
        </el-pagination>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import { errorHandler } from '@/utils/errorHandler.js'
import { mapActions } from 'vuex'
export default {
    name: 'IpLogContent',
    props: [
        'nodeInfo'
    ],
    data () {
        return {
            i18n: {
                error_code: gettext("错误码"),
                placeholder: gettext("请输入 IP")
            },
            loading: true,
            failDetail: '',
            ipTotal: [],
            ipList: [],
            pageSize: 5,
            pageCount: 5,
            ipTableData: [],
            currentRow: null,
            logContent: '',
            dataTotal: [],
            search: ''
        }
    },
    mounted () {
        this.loadIpLogContent()
    },
    watch: {
        search: function () {
            this.dataTotal = this.ipTotal.filter( item => ( !this.search || item.ip.includes(this.search)))
            this.initTable()
        }
    },
    methods: {
        ...mapActions('task/', [
            'getJobInstanceLog'
        ]),
        async loadIpLogContent () {
            this.loading = true
            try {
                if (
                    this.nodeInfo.ex_data &&
                    this.nodeInfo.ex_data.hasOwnProperty('show_ip_log') &&
                    this.nodeInfo.ex_data.show_ip_log
                ) {
                    this.failDetail = await this.getJobInstanceLog({"job_instance_id": this.nodeInfo.ex_data.task_inst_id})
                    this.ipTotal = this.failDetail.data[0].step_results[0].ip_logs
                    this.dataTotal = this.ipTotal
                    this.initTable()
                }
            } catch (e) {
                errorHandler(e, this)
            } finally {
                this.loading = false
            }
        },
        currentChange (val) {
            this.ipList = this.dataTotal.slice(val * this.pageSize - this.pageSize, val * this.pageSize)
        },
        getIpLogContent (data){
            if (data !== null){
                var self = this
                this.ipList.every( item => {
                    if (item.ip === data.ip){
                        self.logContent = item.log_content
                        return false
                    }
                    return true
                })
            }
        },
        setCurrent (row) {
            this.$refs.singleTable.setCurrentRow(row)
        },
        initTable () {
            this.currentChange(1)
            this.getIpLogContent(this.ipList[0])
            this.setCurrent(this.ipList[0])
        }
    }
}
</script>
<style lang="scss" scoped>
.ip-log-content {
    margin-top: 20px;
    height: 360px;
}
.detail-table {
    width: 33%;
    float: left;
}
.detail-ip-log {
    width: 65%;
    height: 360px;
    float: right;
    font-size: 12px;
    background-color: #1c2026;
    border: 1px solid #e4e7ed;
    color: white;
    padding: 4px;
    overflow-y: auto;
}
.pagination {
    float: left;
}
.ip-search {
    width: 33%;
    margin-bottom: 10px;
}
</style>
