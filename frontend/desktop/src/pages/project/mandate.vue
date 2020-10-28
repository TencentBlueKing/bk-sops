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
    <div class="mandate-wrapper">
        <header class="mandate-header">
            <i class="back-icon bk-icon icon-arrows-left" @click="$emit('go-back')"></i>
            <span>{{ $t('成员设置') }}</span>
        </header>
        <section class="mandate-section">
            <div class="title">
                {{ $t('执行代理人设置') }}
                <bk-button theme="primary" @click="onEditAgent">{{ $t('编辑') }}</bk-button>
            </div>
            <bk-form class="agent-form" v-bkloading="{ isLoading: agentLoading, opacity: 1 }">
                <bk-form-item :label="$t('执行代理人')">
                    <div class="user-list">{{ agent.executor_proxy || '--' }}</div>
                </bk-form-item>
                <bk-form-item :label="$t('白名单用户')">
                    <div class="user-list">{{ agent.executor_proxy_exempts || '--' }}</div>
                </bk-form-item>
            </bk-form>
        </section>
        <section class="mandate-section">
            <div class="title">
                {{ $t('人员分组设置') }}
                <bk-button theme="primary" @click="onEditStaffGroup('create')">{{ $t('增加分组') }}</bk-button>
            </div>
            <bk-table :data="staffGroup" class="staff-group-table" v-bkloading="{ isLoading: staffGroupLoading, opacity: 1 }">
                <bk-table-column :label="$t('序号')" :width="150" property="id"></bk-table-column>
                <bk-table-column :label="$t('分组名称')" :width="300" property="name"></bk-table-column>
                <bk-table-column :label="$t('成员')">
                    <template slot-scope="props">
                        {{props.row.members || '--'}}
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t('操作')" :width="300">
                    <template slot-scope="props">
                        <bk-button :text="true" @click="onEditStaffGroup('edit', props.row)">{{ $t('编辑') }}</bk-button>
                        <bk-button :text="true" @click="onDelStaffGroup(props.row)">{{ $t('删除') }}</bk-button>
                    </template>
                </bk-table-column>
                <div class="empty-data" slot="empty"><NoData :message="$t('无数据')" /></div>
            </bk-table>
        </section>
        <bk-dialog
            width="600"
            ext-cls="common-dialog"
            header-position="left"
            render-directive="if"
            :mask-close="false"
            :auto-close="false"
            :title="$t('执行代理人设置')"
            :loading="pending.agent"
            :value="isAgentDialogShow"
            @confirm="updateAgentData"
            @cancel="isAgentDialogShow = false">
            <bk-form class="agent-dialog" :model="editingAgent">
                <bk-form-item :label="$t('执行代理人')">
                    <bk-user-selector
                        v-model="editingAgent.executor_proxy"
                        :api="userApi"
                        :multiple="false">
                    </bk-user-selector>
                </bk-form-item>
                <bk-form-item :label="$t('白名单用户')">
                    <bk-user-selector
                        v-model="editingAgent.executor_proxy_exempts"
                        :fixed-height="false"
                        :api="userApi">
                    </bk-user-selector>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
        <bk-dialog
            width="600"
            ext-cls="common-dialog"
            header-position="left"
            render-directive="if"
            :mask-close="false"
            :auto-close="false"
            :title="$t('人员分组设置')"
            :loading="pending.staff"
            :value="isStaffDialogShow"
            @confirm="editStaffGroupConfirm"
            @cancel="isStaffDialogShow = false">
            <bk-form ref="schemeForm" class="scheme-dialog" :model="staffGroupDetail" :rules="schemeNameRules">
                <bk-form-item property="name" :label="$t('分组名称')" :required="true">
                    <bk-input v-model="staffGroupDetail.name" />
                </bk-form-item>
                <bk-form-item :label="$t('成员')">
                    <bk-user-selector
                        v-model="staffGroupDetail.members"
                        :api="userApi">
                    </bk-user-selector>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
        <bk-dialog
            :mask-close="false"
            :auto-close="false"
            :header-position="'left'"
            :ext-cls="'common-dialog'"
            :title="$t('删除')"
            width="400"
            :value="isDeleteStaffDialogShow"
            @confirm="deleteStaffGroupConfirm"
            @cancel="isDeleteStaffDialogShow = false">
            <div class="delete-dialog" v-bkloading="{ isLoading: pending.delete, opacity: 1 }">
                {{$t('确认删除') + '"' + deletingStaffDetail.name + '"' + '?' }}
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import BkUserSelector from '@blueking/user-selector'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'Mandate',
        components: {
            BkUserSelector,
            NoData
        },
        props: {
            id: Number
        },
        data () {
            return {
                agent: {},
                editingAgent: {},
                isAgentDialogShow: false,
                agentLoading: false,
                staffGroup: [],
                staffGroupDetail: {},
                deletingStaffDetail: {},
                isStaffDialogShow: false,
                isDeleteStaffDialogShow: false,
                staffGroupLoading: false,
                userApi: `${window.MEMBER_SELECTOR_DATA_HOST}/api/c/compapi/v2/usermanage/fs_list_users/`,
                schemeNameRules: {
                    name: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: 50,
                            message: i18n.t('分组名称不能超过50个字符'),
                            trigger: 'blur'
                        }
                    ]
                },
                pending: {
                    agent: false,
                    staff: false,
                    delete: false
                }
            }
        },
        created () {
            this.getAgentData()
            this.getStaffGroupData()
        },
        methods: {
            ...mapActions('project', [
                'getProjectConfig',
                'updateProjectConfig',
                'getProjectStaffGroupList',
                'createProjectStaffGroup',
                'updateProjectStaffGroup',
                'delProjectStaffGroup'
            ]),
            // 获取代理人设置数据
            async getAgentData () {
                this.agentLoading = true
                try {
                    const resp = await this.getProjectConfig(this.id)
                    if (resp.result) {
                        const { executor_proxy, executor_proxy_exempts } = resp.data
                        this.agent = { executor_proxy, executor_proxy_exempts }
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.agentLoading = false
                }
            },
            // 更新代理人数据
            async updateAgentData () {
                if (this.pending.agent) {
                    return
                }
                this.pending.agent = true
                try {
                    const data = {
                        id: this.id,
                        executor_proxy: this.editingAgent.executor_proxy.join(','),
                        executor_proxy_exempts: this.editingAgent.executor_proxy_exempts.join(',')
                    }
                    const resp = await this.updateProjectConfig(data)
                    if (resp.result) {
                        this.isAgentDialogShow = false
                        const { executor_proxy, executor_proxy_exempts } = resp.data
                        this.agent = { executor_proxy, executor_proxy_exempts }
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pending.agent = false
                }
            },
            // 获取人员分组数据
            async getStaffGroupData () {
                this.staffGroupLoading = true
                try {
                    const resp = await this.getProjectStaffGroupList({ project_id: this.id })
                    if (resp.result) {
                        this.staffGroup = resp.data
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.staffGroupLoading = false
                }
            },
            onEditAgent () {
                this.isAgentDialogShow = true
                this.editingAgent = {
                    executor_proxy: this.agent.executor_proxy.split(',').filter(item => item.trim()),
                    executor_proxy_exempts: this.agent.executor_proxy_exempts.split(',').filter(item => item.trim())
                }
            },
            onEditStaffGroup (type, group) {
                let editingData = { name: '', members: [] }
                if (type === 'edit') {
                    const { id, name, members } = group
                    const memberArr = members.split(',').filter(item => item.trim())
                    editingData = { type, id, name, members: memberArr }
                }
                this.staffGroupDetail = editingData
                this.isStaffDialogShow = true
            },
            // 创建、编辑人员分组
            editStaffGroupConfirm () {
                if (this.pending.staff) {
                    return
                }
                this.pending.staff = true
                try {
                    this.$refs.schemeForm.validate().then(async result => {
                        if (result) {
                            let resp
                            const { type, id, name, members } = this.staffGroupDetail
                            const params = {
                                data: {
                                    name,
                                    members: members.join(','),
                                    project_id: this.id
                                }
                            }
                            if (type === 'edit') {
                                params.id = id
                                resp = await this.updateProjectStaffGroup(params)
                            } else {
                                resp = await this.createProjectStaffGroup(params)
                            }
                            if (resp.result) {
                                this.isStaffDialogShow = false
                                this.getStaffGroupData()
                            } else {
                                errorHandler(resp, this)
                            }
                        }
                    })
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pending.staff = false
                }
            },
            onDelStaffGroup (group) {
                this.deletingStaffDetail = { ...group }
                this.isDeleteStaffDialogShow = true
            },
            async deleteStaffGroupConfirm () {
                if (this.pending.staff) {
                    return
                }
                this.pending.staff = true
                try {
                    const resp = await this.delProjectStaffGroup(this.deletingStaffDetail.id)
                    if (resp.result) {
                        this.isDeleteStaffDialogShow = false
                        this.getStaffGroupData()
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pending.staff = false
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .mandate-wrapper {
        min-height: calc(100vh - 240px);
        .mandate-header {
            position: relative;
            padding-left: 38px;
            height: 47px;
            line-height: 46px;
            border-bottom: 1px solid #dcdee5;
            font-size: 14px;
            color: #313238;
            .back-icon {
                position: absolute;
                left: 10px;
                top: 8px;
                font-size: 30px;
                color: #3a84ff;
                cursor: pointer;
            }
        }
        .mandate-section {
            padding: 32px;
            .title {
                position: relative;
                margin: 0 0 10px;
                padding-bottom: 10px;
                font-size: 14px;
                line-height: 1;
                border-bottom: 1px solid #cacedb;
                .bk-button {
                    position: absolute;
                    right: 0;
                    top: -18px;
                    width: 80px;
                }
            }
            .agent-form {
                margin-top: 20px;
            }
            .user-list {
                width: 80%;
                font-size: 12px;
                color: #63656e;
                word-break: break-all;
            }
        }
        .staff-group-table {
            background: #fff;
        }
    }
    .agent-dialog,
    .scheme-dialog,
    .delete-dialog {
        padding: 30px;
        word-break: break-all;
        /deep/ .bk-form-content {
            margin-right: 30px;
        }
        .user-selector {
            width: 100%;
        }
    }
</style>
