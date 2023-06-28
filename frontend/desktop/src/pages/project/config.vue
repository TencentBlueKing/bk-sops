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
    <div class="mandate-wrapper">
        <page-header class="mandate-header">
            <i class="back-icon bk-icon icon-arrows-left" @click="$router.push({ name: 'projectHome' })"></i>
            <span>{{ $t('项目配置') }}</span>
        </page-header>
        <div class="mandate-page-content">
            <section
                class="project-info"
                data-test-id="projectConfig_form_projectInfo"
                v-bkloading="{ isLoading: projectLoading, opacity: 1, zIndex: 100 }">
                <template v-if="project.name">
                    <div class="icon">{{ project.name[0] }}</div>
                </template>
                <div class="info-wrap">
                    <div class="title">
                        <h4>{{ project.name }}</h4>
                        <div class="ext-info">
                            <span>ID <span class="value">{{ project.id }}</span></span>
                            <span>CC_ID <span class="value">{{ project.bk_biz_id }}</span></span>
                            <span>{{ $t('时区') }} <span class="value">{{ project.time_zone }}</span></span>
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
            <section class="mandate-section" data-test-id="projectConfig_form_executeAgent">
                <div class="title">
                    {{ $t('执行代理人设置') }}
                    <bk-button
                        theme="primary"
                        data-test-id="projectConfig_form_editExecuteAgent"
                        @click="onEditAgent">
                        {{ $t('编辑') }}
                    </bk-button>
                </div>
                <bk-form class="agent-form" :label-width="180" v-bkloading="{ isLoading: agentLoading, opacity: 1, zIndex: 100 }">
                    <bk-form-item :label="$t('执行代理人')">
                        <div class="user-list">{{ agent.executor_proxy || '--' }}</div>
                    </bk-form-item>
                    <bk-form-item :label="$t('免代理用户')">
                        <div class="user-list">{{ agent.executor_proxy_exempts || '--' }}</div>
                    </bk-form-item>
                </bk-form>
            </section>
            <bk-tab :active.sync="active" type="unborder-card" @tab-change="handleTabChange">
                <bk-tab-panel :label="$t('人员分组设置')" name="staffing_group_settings">
                    <section class="mandate-section">
                        <div class="title">
                            {{ $t('人员分组设置') }}({{ staffGroup.length }})
                            <bk-button theme="primary" @click="onEditStaffGroup('create')">{{ $t('增加分组') }}</bk-button>
                        </div>
                        <bk-table :data="staffGroup" v-bkloading="{ isLoading: staffGroupLoading, opacity: 1, zIndex: 100 }">
                            <bk-table-column :label="$t('序号')" show-overflow-tooltip :width="150" property="id"></bk-table-column>
                            <bk-table-column :label="$t('分组名称')" show-overflow-tooltip :width="300" property="name" :render-header="renderTableHeader"></bk-table-column>
                            <bk-table-column :label="$t('成员')" show-overflow-tooltip>
                                <template slot-scope="props">
                                    {{props.row.members || '--'}}
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t('操作')" :width="300">
                                <template slot-scope="props">
                                    <bk-button :text="true" @click="onEditStaffGroup('edit', props.row)">{{ $t('编辑') }}</bk-button>
                                    <bk-button :text="true" class="ml10" @click="onDelStaffGroup(props.row)">{{ $t('删除') }}</bk-button>
                                </template>
                            </bk-table-column>
                            <div class="empty-data" slot="empty">
                                <NoData></NoData>
                            </div>
                        </bk-table>
                    </section>
                </bk-tab-panel>
                <bk-tab-panel :label="$t('标签设置')" name="label_config">
                    <section class="mandate-section">
                        <div class="title">
                            {{ $t('标签设置') }}({{ labelList.length }})
                            <bk-button theme="primary" @click="onEditLabel('create')">{{ $t('新增标签') }}</bk-button>
                        </div>
                        <bk-table :data="labelList" v-bkloading="{ isLoading: labelLoading, opacity: 1, zIndex: 100 }">
                            <bk-table-column :label="$t('标签名称')" property="name" :min-width="150" show-overflow-tooltip :render-header="renderTableHeader">
                                <template slot-scope="props">
                                    <span class="label-name"
                                        :style="{ background: props.row.color, color: darkColorList.includes(props.row.color) ? '#fff' : '#262e4f' }">
                                        {{ props.row.name }}</span>
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t('标签描述')" :min-width="300" show-overflow-tooltip :render-header="renderTableHeader">
                                <template slot-scope="props">
                                    {{ props.row.description || '--' }}
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t('标签引用')" :width="200" show-overflow-tooltip :render-header="renderTableHeader">
                                <template slot-scope="props">
                                    <router-link
                                        class="citation"
                                        :to="{
                                            name: 'processHome',
                                            params: { project_id: id },
                                            query: { label_ids: String(props.row.id) }
                                        }">
                                        {{ labelCount[props.row.id] || 0 }}
                                    </router-link>
                                    {{ $t('个流程在引用') }}
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t('系统默认标签')" :width="300" :render-header="renderTableHeader">
                                <template slot-scope="props">
                                    {{ props.row.is_default ? $t('是') : $t('否') }}
                                </template>
                            </bk-table-column>
                            <bk-table-column :label="$t('操作')" :width="200">
                                <template slot-scope="props">
                                    <bk-popover :disabled="!props.row.is_default" :content="$t('默认标签不支持编辑删除')">
                                        <bk-button :text="true" :disabled="props.row.is_default" @click="onEditLabel('edit', props.row)">
                                            {{ $t('编辑') }}
                                        </bk-button>
                                    </bk-popover>
                                    <bk-popover :disabled="!props.row.is_default" :content="$t('默认标签不支持编辑删除')">
                                        <bk-button :text="true" class="ml10" :disabled="props.row.is_default" @click="onDelLabel(props.row)">
                                            {{ $t('删除') }}
                                        </bk-button>
                                    </bk-popover>
                                </template>
                            </bk-table-column>
                            <div class="empty-data" slot="empty">
                                <NoData></NoData>
                            </div>
                        </bk-table>
                    </section>
                </bk-tab-panel>
                <bk-tab-panel :label="$t('project_项目变量')" name="variable">
                    <section class="mandate-section">
                        <div class="variable-list">
                            <p class="variable-list-tip">{{ $t('项目级别的变量建立后,可以在模板中通过${_env_key}方式引用') }}</p>
                            <bk-button :theme="'primary'" @click="onAddVariable('create')">{{ $t('新增项目变量') }}</bk-button>
                        </div>
                        <bk-table style="margin-top: 15px;" :data="variableData">
                            <bk-table-column show-overflow-tooltip :label="$t('变量名称')" prop="name" :render-header="renderTableHeader"></bk-table-column>
                            <bk-table-column show-overflow-tooltip :label="$t('Key')" prop="key"></bk-table-column>
                            <bk-table-column show-overflow-tooltip :label="$t('值')" prop="value"></bk-table-column>
                            <bk-table-column show-overflow-tooltip :label="$t('说明')" prop="desc"></bk-table-column>
                            <bk-table-column :label="$t('操作')">
                                <template slot-scope="props">
                                    <bk-button theme="primary" text @click="onAddVariable('edit', props.row)">{{ $t('编辑') }}</bk-button>
                                    <bk-button theme="primary" class="ml10" text @click="onRemove(props.row)">{{ $t('删除') }}</bk-button>
                                </template>
                            </bk-table-column>
                            <div class="empty-data" slot="empty">
                                <NoData></NoData>
                            </div>
                        </bk-table>
                    </section>
                </bk-tab-panel>
            </bk-tab>
        </div>
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
            data-test-id="projectConfig_form_executeAgentDialog"
            :cancel-text="$t('取消')"
            @confirm="updateAgentData"
            @cancel="isAgentDialogShow = false">
            <bk-form class="agent-dialog" :model="editingAgent" :label-width="180">
                <bk-form-item :label="$t('执行代理人')">
                    <bk-user-selector
                        v-model="editingAgent.executor_proxy"
                        :placeholder="$t('请输入用户')"
                        :api="userApi"
                        :multiple="false">
                    </bk-user-selector>
                </bk-form-item>
                <bk-form-item :label="$t('免代理用户')">
                    <bk-user-selector
                        v-model="editingAgent.executor_proxy_exempts"
                        :placeholder="$t('请输入用户')"
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
            :title="$t('new_人员分组设置')"
            :loading="pending.staff"
            :value="isStaffDialogShow"
            :cancel-text="$t('取消')"
            @confirm="editStaffGroupConfirm"
            @cancel="isStaffDialogShow = false">
            <bk-form ref="schemeForm" class="scheme-dialog" :model="staffGroupDetail" :rules="schemeNameRules">
                <bk-form-item property="name" :label="$t('分组名称')" :required="true">
                    <bk-input v-model="staffGroupDetail.name" />
                </bk-form-item>
                <bk-form-item :label="$t('成员')">
                    <bk-user-selector
                        v-model="staffGroupDetail.members"
                        :placeholder="$t('请输入用户')"
                        :api="userApi">
                    </bk-user-selector>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
        <bk-dialog
            width="600"
            ext-cls="common-dialog label-dialog"
            header-position="left"
            render-directive="if"
            :mask-close="false"
            :auto-close="false"
            :title="$t('new_标签设置')"
            :loading="pending.label"
            :value="isLabelDialogShow"
            :cancel-text="$t('取消')"
            @confirm="editLabelConfirm"
            @cancel="isLabelDialogShow = false">
            <bk-form ref="labelForm" :model="labelDetail" :rules="labelRules">
                <bk-form-item property="name" :label="$t('标签名称')" :required="true">
                    <bk-input v-model="labelDetail.name"></bk-input>
                </bk-form-item>
                <bk-form-item property="color" :label="$t('标签颜色')" :required="true">
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
                <bk-form-item :label="$t('标签描述')">
                    <bk-input type="textarea" v-model="labelDetail.description"></bk-input>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
        <!-- 新增变量 -->
        <bk-dialog
            :mask-close="false"
            :auto-close="false"
            width="636"
            :ext-cls="'create-variable-dialog'"
            :title="$t('环境变量设置')"
            :header-position="'left'"
            :loading="pending.variable"
            :value="isAddVariableDialogShow"
            :cancel-text="$t('取消')"
            @confirm="variableConfirm"
            @cancel="isAddVariableDialogShow = false">
            <bk-form class="create-variable-form" :label-width="100" ref="variableForm" :model="variableFormData" :rules="variableRules">
                <bk-form-item class="form-item-name" :label="$t('变量名称')" :required="true" property="name">
                    <bk-input v-model="variableFormData.name" :placeholder="$t('请输入变量名称')"></bk-input>
                </bk-form-item>
                <bk-form-item class="form-item-key" label="Key" :required="true" property="key">
                    <bk-input v-model="variableFormData.key" :placeholder="$t('变量KEY由英文字母、数字、下划线组成，且不能以数字开头')"></bk-input>
                </bk-form-item>
                <bk-form-item class="form-item-value" :label="$t('值')" :required="true" property="value">
                    <bk-input type="textarea" v-model="variableFormData.value" :placeholder="$t('请填写变量值')"></bk-input>
                </bk-form-item>
                <bk-form-item class="form-item-desc" :label="$t('说明')" :required="true" property="desc">
                    <bk-input type="textarea" v-model="variableFormData.desc" :placeholder="$t('请填入项目变量说明')"></bk-input>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import BkUserSelector from '@blueking/user-selector'
    import { LABEL_COLOR_LIST, DARK_COLOR_LIST } from '@/constants/index.js'
    import { mapActions, mapState } from 'vuex'
    import permission from '@/mixins/permission.js'
    import PageHeader from '@/components/layout/PageHeader.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'Mandate',
        components: {
            BkUserSelector,
            PageHeader,
            NoData
        },
        mixins: [permission],
        props: {
            id: [Number, String]
        },
        data () {
            return {
                variableData: [],
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
                isStaffDialogShow: false,
                staffGroupLoading: false,
                labelList: [],
                labelLoading: false,
                isLabelDialogShow: false,
                labelDetail: {},
                labelCount: {},
                userApi: `${window.MEMBER_SELECTOR_DATA_HOST}/api/c/compapi/v2/usermanage/fs_list_users/`,
                colorDropdownShow: false,
                colorList: LABEL_COLOR_LIST,
                darkColorList: DARK_COLOR_LIST,
                variableRules: {
                    name: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: 50,
                            message: i18n.t('变量name值长度不能超过') + '50',
                            trigger: 'blur'
                        },
                        {
                            regex: /^[^'"‘’“”$<>]+$/,
                            message: i18n.t('变量name不能包含特殊字符'),
                            trigger: 'blur'
                        }
                    ],
                    key: [
                        {
                            required: true,
                            message: i18n.t('变量KEY值不能为空'),
                            trigger: 'blur'
                        },
                        {
                            regex: /(^\${[a-zA-Z_]\w*}$)|(^[a-zA-Z_]\w*$)/,
                            message: i18n.t('变量KEY由英文字母、数字、下划线组成，且不能以数字开头'),
                            trigger: 'blur'
                        },
                        {
                            max: 50,
                            message: i18n.t('变量KEY值长度不能超过') + '50',
                            trigger: 'blur'
                        }
                    ],
                    value: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        }
                    ],
                    desc: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        }
                    ]
                },
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
                        },
                        {
                            validator: (val) => {
                                return this.labelList.every(label => this.labelDetail.id === label.id || label.name !== val)
                            },
                            message: i18n.t('标签已存在，请重新输入'),
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
                    deleteLabel: false,
                    variable: false,
                    deletevariable: false
                },
                active: 'variable',
                isAddVariableDialogShow: false,
                variableFormData: {
                    name: '',
                    key: '',
                    value: '',
                    desc: ''
                }
            }
        },
        computed: {
            ...mapState({
                username: state => state.username
            })
        },
        created () {
            const { configActive } = this.$route.query
            this.active = configActive || 'variable'
            this.getProjectDetail()
            this.getAgentData()
            this.getStaffGroupData()
            this.getTplLabels()
            this.getVariableData()
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
                'getProjectLabelsWithDefault',
                'updateTemplateLabel',
                'createTemplateLabel',
                'delTemplateLabel',
                'getLabelsCitedCount',
                'loadEnvVariableList',
                'createEnvVariable',
                'deleteEnvVariable',
                'updateEnvVariable'
            ]),
            async getVariableData () {
                const data = {
                    project_id: this.$route.params.id
                }
                const resp = await this.loadEnvVariableList(data)
                if (resp.result) {
                    this.variableData = resp.data
                }
            },
            async getProjectDetail () {
                this.projectLoading = true
                try {
                    this.project = await this.loadProjectDetail(this.id)
                    this.descData.value = this.project.desc
                } catch (e) {
                    console.log(e)
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
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.agentLoading = false
                }
            },
            renderTableHeader (h, { column, $index }) {
                return h('p', {
                    class: 'label-text',
                    directives: [{
                        name: 'bk-overflow-tips'
                    }]
                }, [
                    column.label
                ])
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
                            const { id, name, time_zone } = this.project
                            const data = {
                                id,
                                name,
                                time_zone,
                                desc: this.descData.value
                            }
                            this.project = await this.updateProject(data)
                            this.descEditing = false
                        } catch (e) {
                            console.log(e)
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
                    }
                } catch (e) {
                    console.log(e)
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
                    }
                } catch (e) {
                    console.log(e)
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
            handleTabChange (name) {
                this.$router.replace({
                    name: 'projectConfig',
                    query: {
                        configActive: name
                    }
                })
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
                            }
                        }
                    })
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.staff = false
                }
            },
            onDelStaffGroup (group) {
                const h = this.$createElement
                this.$bkInfo({
                    subHeader: h('div', { class: 'custom-header' }, [
                        h('div', {
                            class: 'custom-header-title',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('确认删除') + i18n.t('分组') + '"' + group.name + '"?'])
                    ]),
                    extCls: 'dialog-custom-header-title',
                    maskClose: false,
                    confirmLoading: true,
                    cancelText: this.$t('取消'),
                    confirmFn: async () => {
                        await this.deleteStaffGroupConfirm(group)
                    }
                })
            },
            async deleteStaffGroupConfirm (group) {
                if (this.pending.staff) {
                    return
                }
                this.pending.staff = true
                try {
                    const resp = await this.delProjectStaffGroup(group.id)
                    if (resp.result) {
                        this.getStaffGroupData()
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.staff = false
                }
            },
            async getTplLabels () {
                this.labelLoading = true
                this.labelCount = {}
                try {
                    const resp = await this.getProjectLabelsWithDefault(this.id)
                    if (resp.result) {
                        const defaultList = []
                        const normalList = []
                        resp.data.forEach(item => {
                            item.is_default ? defaultList.push(item) : normalList.push(item)
                        })
                        this.labelList = [...normalList, ...defaultList]
                        if (resp.data.length > 0) {
                            const ids = resp.data.map(item => item.id).join(',')
                            const labelData = await this.getLabelsCitedCount({ ids, project_id: this.id })
                            if (labelData.result) {
                                this.labelCount = labelData.data
                            }
                        }
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.labelLoading = false
                }
            },
            onEditLabel (type, label) {
                this.labelDetail = type === 'edit' ? { ...label, type: 'edit' } : { color: '#1c9574', name: '', description: '' }
                this.isLabelDialogShow = true
                this.colorDropdownShow = false
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
                            }
                        }
                    })
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.label = false
                }
            },
            onDelLabel (label) {
                const h = this.$createElement
                this.$bkInfo({
                    subHeader: h('div', { class: 'custom-header' }, [
                        h('div', {
                            class: 'custom-header-title',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('确认删除该标签?')]),
                        h('div', {
                            class: 'custom-header-sub-title bk-dialog-header-inner',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('关联的流程将同时移除本标签')])
                    ]),
                    extCls: 'dialog-custom-header-title',
                    maskClose: false,
                    confirmLoading: true,
                    cancelText: this.$t('取消'),
                    confirmFn: async () => {
                        await this.deleteLabelGroupConfirm(label)
                    }
                })
            },
            async deleteLabelGroupConfirm (label) {
                if (this.pending.deleteLabel) {
                    return
                }
                this.pending.deleteLabel = true
                try {
                    const resp = await this.delTemplateLabel(label.id)
                    if (resp.result) {
                        this.getTplLabels()
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.deleteLabel = false
                }
            },
            onAddVariable (type, rows) {
                this.variableFormData = type === 'edit' ? { ...rows, type: 'edit', id: rows.id } : { name: '', key: '', value: '', desc: '' }
                this.isAddVariableDialogShow = true
                this.$refs.variableForm.clearError()
            },
            variableConfirm () {
                if (this.pending.variable) {
                    return
                }
                this.pending.variable = true
                try {
                    this.$refs.variableForm.validate().then(async validator => {
                        if (validator) {
                            const { type, name, key, desc, value, id } = this.variableFormData
                            const data = {
                                name,
                                project_id: this.$route.params.id,
                                key,
                                value,
                                desc,
                                id
                            }
                            const resp = type ? await this.updateEnvVariable(data) : await this.createEnvVariable(data)
                            if (resp.result) {
                                this.getVariableData()
                                this.isAddVariableDialogShow = false
                            }
                        }
                    })
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.variable = false
                }
            },
            onRemove (variable) {
                const h = this.$createElement
                this.$bkInfo({
                    subHeader: h('div', { class: 'custom-header' }, [
                        h('div', {
                            class: 'custom-header-title',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('确认删除') + i18n.t('project_项目变量') + `"${variable.key}"?`]),
                        h('div', {
                            class: 'custom-header-sub-title bk-dialog-header-inner',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('若该变量被流程的节点引用，请及时检查并更新节点配置')])
                    ]),
                    extCls: 'dialog-custom-header-title',
                    maskClose: false,
                    confirmLoading: true,
                    cancelText: this.$t('取消'),
                    confirmFn: async () => {
                        await this.onDeleteVariable(variable)
                    }
                })
            },
            async onDeleteVariable (variable) {
                if (this.pending.deletevariable) {
                    return
                }
                this.pending.deletevariable = true
                try {
                    await this.deleteEnvVariable(variable.id)
                    this.getVariableData()
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending.deletevariable = false
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    .mandate-wrapper {
        min-height: calc(100vh - 52px);
        .mandate-header {
            display: flex;
            align-items: center;
            padding-left: 10px;
            .back-icon {
                font-size: 28px;
                color: #3a84ff;
                cursor: pointer;
            }
        }
        .mandate-page-content {
            padding: 0 20px;
            height: calc(100vh - 100px);
            overflow: auto;
            @include scrollbar;
        }
        .project-info {
            display: flex;
            justify-content: flex-start;
            padding: 40px 0;
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
            padding: 32px 0;
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
            .variable-list {
                display: flex;
                justify-content: space-between;
                .variable-list-tip {
                    font-size: 14px;
                }
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
    .citation {
        color: #3a84ff;
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
    .create-variable-dialog {
        .create-variable-form {
            display: flex;
            flex-direction: column;
        }
    }
</style>
