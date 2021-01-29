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
            <i class="back-icon bk-icon icon-arrows-left" @click="$router.push({ name: 'projectHome' })"></i>
            <span>{{ $t('项目配置') }}</span>
        </header>
        <section class="project-info" v-bkloading="{ isLoading: projectLoading, opacity: 1 }">
            <template v-if="project.name">
                <div class="icon">{{ project.name[0] }}</div>
            </template>
            <div class="info-wrap">
                <div class="title">
                    <h4>{{ project.name }}</h4>
                    <div class="ext-info">
                        <span>ID <span class="value">{{ project.id }}</span></span>
                        <span>CC_ID <span class="value">{{ project.bk_biz_id }}</span></span>
                        <span>时区 <span class="value">{{ project.time_zone }}</span></span>
                    </div>
                </div>
                <div class="desc">
                    <template v-if="!descEditing">
                        <span>{{ project.desc || '--' }}</span>
                        <span
                            v-cursor="{ active: !hasPermission(['project_edit'], project.auth_actions) }"
                            class="common-icon-edit icon-btn"
                            :class="{ 'text-permission-disable': !hasPermission(['project_edit'], project.auth_actions) }"
                            @click="onOpenDescEdit">
                        </span>
                    </template>
                    <bk-form v-else ref="descForm" :model="descData" :rules="descRules">
                        <bk-form-item :label-width="0" property="value">
                            <bk-input
                                ref="descInput"
                                type="textarea"
                                :rows="4"
                                v-model="descData.value"
                                @blur="onEditDesc">
                            </bk-input>
                        </bk-form-item>
                    </bk-form>
                </div>
            </div>
        </section>
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
                {{ $t('人员分组设置') }}({{ staffGroup.length }})
                <bk-button theme="primary" @click="onEditStaffGroup('create')">{{ $t('增加分组') }}</bk-button>
            </div>
            <bk-table :data="staffGroup" v-bkloading="{ isLoading: staffGroupLoading, opacity: 1 }">
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
            </bk-table>
        </section>
        <section class="mandate-section">
            <div class="title">
                {{ $t('标签设置') }}({{ labelList.length }})
                <bk-button theme="primary" @click="onEditLabel('create')">{{ $t('新增标签') }}</bk-button>
            </div>
            <bk-table :data="labelList" v-bkloading="{ isLoading: labelLoading, opacity: 1 }">
                <bk-table-column :label="$t('标签名称')" property="name" :width="150">
                    <template slot-scope="props">
                        <span class="label-name" :style="{ background: props.row.color }">{{ props.row.name }}</span>
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t('标签描述')" :width="300">
                    <template slot-scope="props">
                        {{ props.row.description || '--' }}
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t('标签引用')">
                    <template slot-scope="props">
                        {{ labelCount[props.row.id] ? labelCount[props.row.id].length : 0 }}{{ $t('个流程在引用') }}
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t('系统默认标签')" :width="300">
                    <template slot-scope="props">
                        {{ props.row.is_default ? $t('是') : $t('否') }}
                    </template>
                </bk-table-column>
                <bk-table-column :label="$t('操作')" :width="300">
                    <template slot-scope="props">
                        <bk-button :text="true" :disabled="props.row.is_default" @click="onEditLabel('edit', props.row)">{{ $t('编辑') }}</bk-button>
                        <bk-button :text="true" :disabled="props.row.is_default" @click="onDelLabel(props.row)">{{ $t('删除') }}</bk-button>
                    </template>
                </bk-table-column>
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
            :loading="pending.delete"
            :value="isDeleteStaffDialogShow"
            @confirm="deleteStaffGroupConfirm"
            @cancel="isDeleteStaffDialogShow = false">
            <div class="delete-dialog">
                {{$t('确认删除') + '"' + deletingStaffDetail.name + '"' + '?' }}
            </div>
        </bk-dialog>
        <bk-dialog
            width="600"
            ext-cls="common-dialog"
            header-position="left"
            render-directive="if"
            :mask-close="false"
            :auto-close="false"
            :title="$t('标签设置')"
            :loading="pending.label"
            :value="isLabelDialogShow"
            @confirm="editLabelConfirm"
            @cancel="isLabelDialogShow = false">
            <bk-form ref="labelForm" class="label-dialog" :model="labelDetail" :rules="labelRules">
                <bk-form-item property="color" :label="$t('颜色')" :required="true">
                    <bk-dropdown-menu
                        ref="dropdown"
                        trigger="click"
                        class="color-dropdown"
                        @show="colorDropdownShow = true"
                        @hide="colorDropdownShow = false">
                        <div class="dropdown-trigger-btn" slot="dropdown-trigger">
                            <span class="color-block" :style="{ background: labelDetail.color }"></span>
                            <i :class="['bk-icon icon-angle-down',{ 'icon-flip': colorDropdownShow }]"></i>
                        </div>
                        <div class="color-list" slot="dropdown-content">
                            <div class="tip">{{ $t('选择颜色') }}</div>
                            <div>
                                <span
                                    v-for="color in colorList"
                                    :key="color"
                                    class="color-item color-block"
                                    :style="{ background: color }"
                                    @click="labelDetail.color = color">
                                </span>
                            </div>
                        </div>
                    </bk-dropdown-menu>
                </bk-form-item>
                <bk-form-item property="name" :label="$t('名称')" :required="true">
                    <bk-input v-model="labelDetail.name"></bk-input>
                </bk-form-item>
                <bk-form-item :label="$t('描述')">
                    <bk-input type="textarea" v-model="labelDetail.description"></bk-input>
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
            :loading="pending.deleteLabel"
            :value="isDeleteLabelDialogShow"
            @confirm="deleteLabelGroupConfirm"
            @cancel="isDeleteLabelDialogShow = false">
            <div class="delete-dialog">
                {{$t('确认删除') + '"' + deletingLabelDetail.name + '"' + '?' }}
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import BkUserSelector from '@blueking/user-selector'
    import { mapActions, mapState } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import permission from '@/mixins/permission.js'

    export default {
        name: 'Mandate',
        components: {
            BkUserSelector
        },
        mixins: [permission],
        props: {
            id: [Number, String]
        },
        data () {
            return {
                projectLoading: false,
                project: {},
                descEditing: false,
                descData: { value: '' },
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
                labelList: [],
                labelLoading: false,
                isLabelDialogShow: false,
                deletingLabelDetail: {},
                isDeleteLabelDialogShow: false,
                labelDetail: {},
                labelCount: {},
                userApi: `${window.MEMBER_SELECTOR_DATA_HOST}/api/c/compapi/v2/usermanage/fs_list_users/`,
                colorDropdownShow: false,
                colorList: [
                    '#c4c6cc', '#ffd695', '#ffdddd', '#e1ecff', '#dcffe2',
                    '#c4c6cc', '#ffd695', '#fd9c9c', '#a3c5fd', '#94f5a4',
                    '#979ba5', '#ffb848', '#ff5656', '#699df4', '#45e35f'
                ],
                descRules: {
                    value: [{
                        max: 512,
                        message: i18n.t('项目描述不能超过') + 512 + i18n.t('个字符'),
                        trigger: 'blur'
                    }]
                },
                schemeNameRules: {
                    name: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: 50,
                            message: i18n.t('分组名称不能超过') + 50 + i18n.t('个字符'),
                            trigger: 'blur'
                        }
                    ]
                },
                labelRules: {
                    color: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        }
                    ],
                    name: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: 50,
                            message: i18n.t('标签名称不能超过') + 50 + i18n.t('个字符'),
                            trigger: 'blur'
                        }
                    ]
                },
                pending: {
                    desc: false,
                    agent: false,
                    staff: false,
                    delete: false,
                    label: false,
                    deleteLabel: false
                }
            }
        },
        computed: {
            ...mapState({
                username: state => state.username
            })
        },
        created () {
            this.getProjectDetail()
            this.getAgentData()
            this.getStaffGroupData()
            this.getTplLabels()
        },
        methods: {
            ...mapActions('project', [
                'loadProjectDetail',
                'getProjectConfig',
                'updateProject',
                'updateProjectConfig',
                'getProjectStaffGroupList',
                'createProjectStaffGroup',
                'updateProjectStaffGroup',
                'delProjectStaffGroup',
                'getProjectLabels',
                'updateTemplateLabel',
                'createTemplateLabel',
                'delTemplateLabel',
                'getlabelsCitedCount'
            ]),
            async getProjectDetail () {
                this.projectLoading = true
                try {
                    this.project = await this.loadProjectDetail(this.id)
                    this.descData.value = this.project.desc
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.projectLoading = false
                }
            },
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
            onOpenDescEdit () {
                if (!this.hasPermission(['project_edit'], this.project.auth_actions)) {
                    const resourceData = {
                        project: [{
                            id: this.project.id,
                            name: this.project.name
                        }]
                    }
                    this.applyForPermission(['project_edit'], this.project.auth_actions, resourceData)
                    return
                }
                this.descEditing = true
                this.$nextTick(() => {
                    this.$refs.descInput.focus()
                })
            },
            onEditDesc () {
                this.$refs.descForm.validate().then(async result => {
                    if (result) {
                        if (this.pending.desc) {
                            return
                        }
                        this.pending.desc = true
                        try {
                            const { id, name, timeZone: time_zone } = this.project
                            const data = {
                                id,
                                name,
                                time_zone,
                                desc: this.descData.value
                            }
                            this.project = await this.updateProject(data)
                            this.descEditing = false
                        } catch (err) {
                            errorHandler(err, this)
                        } finally {
                            this.pending.desc = false
                        }
                    }
                })
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
            },
            async getTplLabels () {
                this.labelLoading = true
                this.labelCount = {}
                try {
                    const resp = await this.getProjectLabels(this.id)
                    this.labelList = resp.data
                    if (resp.data.length > 0) {
                        const ids = resp.data.map(item => item.id).join(',')
                        const labelData = await this.getlabelsCitedCount(ids)
                        this.labelCount = labelData.data
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.labelLoading = false
                }
            },
            onEditLabel (type, label) {
                this.labelDetail = type === 'edit' ? { ...label, type: 'edit' } : { color: '#dcffe2', name: '', description: '' }
                this.isLabelDialogShow = true
            },
            onSelectColor (val) {
                this.labelDetail.color = val
            },
            editLabelConfirm () {
                if (this.pending.label) {
                    return
                }
                this.pending.label = true
                try {
                    this.$refs.labelForm.validate().then(async result => {
                        if (result) {
                            let resp
                            const { type, color, name, description, id } = this.labelDetail
                            const data = {
                                creator: this.username,
                                project_id: Number(this.id),
                                color,
                                name,
                                description
                            }
                            if (type === 'edit') {
                                data.id = id
                                resp = await this.updateTemplateLabel(data)
                            } else {
                                resp = await this.createTemplateLabel(data)
                            }
                            if (resp.result) {
                                this.isLabelDialogShow = false
                                this.getTplLabels()
                            } else {
                                errorHandler(resp, this)
                            }
                        }
                    })
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pending.label = false
                }
            },
            onDelLabel (label) {
                this.deletingLabelDetail = { ...label }
                this.isDeleteLabelDialogShow = true
            },
            async deleteLabelGroupConfirm () {
                if (this.pending.deleteLabel) {
                    return
                }
                this.pending.deleteLabel = true
                try {
                    const resp = await this.delTemplateLabel(this.deletingLabelDetail.id)
                    if (resp.result) {
                        this.isDeleteLabelDialogShow = false
                        this.getTplLabels()
                    } else {
                        errorHandler(resp, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.pending.deleteLabel = false
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .mandate-wrapper {
        background: #ffffff;
        min-height: calc(100vh - 50px);
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
        .project-info {
            display: flex;
            justify-content: flex-start;
            padding: 40px 32px;
            background: #f4f7fa;
            .icon {
                margin-right: 16px;
                width: 56px;
                height: 56px;
                line-height: 56px;
                font-size: 30px;
                font-weight: bold;
                color: #ffffff;
                text-align: center;
                background: #ff5656;
                border-radius: 2px;
            }
            .title {
                display: flex;
                justify-content: flex-start;
                align-items: center;
                h4 {
                    margin: 0 20px 0 0;
                    font-size: 18px;
                }
                .ext-info {
                    font-size: 12px;
                    color: #64666f;
                    .value {
                        color: #313238;
                    }
                    &>span {
                        margin-right: 20px;
                    }
                }
            }
            .desc {
                margin-top: 10px;
                color: #63666f;
                font-size: 12px;
                .icon-btn {
                    font-size: 14px;
                    color: #979ba5;
                    cursor: pointer;
                    &:hover {
                        color: #3a84ff;
                    }
                }
                /deep/ .bk-form-content {
                    margin-left: 0 !important;
                    width: 600px;
                }
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
        .bk-table {
            background: #fff;
        }
    }
    .label-name {
        display: inline-block;
        padding: 2px 6px;
        font-size: 12px;
        line-height: 1;
        color: #63656e;
        border-radius: 8px;
    }
    .agent-dialog,
    .scheme-dialog,
    .delete-dialog,
    .label-dialog {
        padding: 30px;
        word-break: break-all;
        /deep/ .bk-form-content {
            margin-right: 30px;
        }
        .user-selector {
            width: 100%;
        }
    }
    .color-dropdown {
        .dropdown-trigger-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0 7px;
            height: 32px;
            border: 1px solid #c4c6cc;
            border-radius: 2px;
            cursor: pointer;
            &>i {
                margin: 0 6px;
                font-size: 16px;
            }
        }
        .color-block {
            display: inline-block;
            width: 20px;
            height: 20px;
        }
        .color-list {
            width: 148px;
            padding: 6px 16px 6px;
            overflow: hidden;
            .tip {
                margin-bottom: 10px;
                color: #b2bed4;
                font-size: 12px;
                line-height: 1;
            }
            .color-item {
                float: left;
                margin-right: 4px;
                margin-bottom: 4px;
                cursor: pointer;
                &:nth-child(5n) {
                    margin-right: 0;
                }
            }
        }
    }
</style>
