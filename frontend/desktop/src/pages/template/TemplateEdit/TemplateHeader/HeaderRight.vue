<template>
    <div class="header-right">
        <template v-if="type === 'view'">
            <div class="tab-operate" @click="$emit('onChangePanel', 'executeSchemaTab')">
                <i class="common-icon-file-setting"></i>
                {{ '执行方案' }}
            </div>
            <div class="tab-operate" @click="$emit('onChangePanel', 'executeSettingTab')">
                <i class="common-icon-file-setting"></i>
                {{ '执行设置' }}
            </div>
            <div class="tab-operate" @click="$emit('onChangePanel', 'operateFlowTab')">
                <i class="common-icon-file-setting"></i>
                {{ '操作流水' }}
            </div>
            <bk-button
                v-if="isViewMode && !isProjectCommonTemp"
                theme="primary"
                :class="['task-btn', {
                    'btn-permission-disable': !editBtnActive
                }]"
                v-cursor="{ active: !editBtnActive }"
                data-test-id="templateEdit_form_editCanvas"
                @click.stop="onEditClick">
                {{$t('编辑')}}
            </bk-button>
            <bk-button
                :class="['task-btn create-btn', {
                    'btn-permission-disable': !createTaskBtnActive
                }]"
                v-cursor="{ active: !createTaskBtnActive }"
                data-test-id="templateEdit_form_createTask"
                @click.stop="onCreateTask">
                {{$t('新建任务')}}
            </bk-button>
        </template>
        <template v-else>
            <div class="recently-text">
                {{ '最近保存：' + 'ddddddd' + ' ' + '10-02' + ' ' + '10:45:41' }}
            </div>
            <bk-button
                :class="['task-btn', {
                    'btn-permission-disable': !saveBtnActive
                }]"
                v-cursor="{ active: !saveBtnActive }"
                data-test-id="templateEdit_form_editCanvas"
                @click.stop="onEditClick">
                {{$t('保存草稿')}}
            </bk-button>
            <bk-button
                theme="primary"
                :class="['task-btn release-btn', {
                    'btn-permission-disable': !saveBtnActive
                }]"
                :loading="templateSaving"
                v-cursor="{ active: !saveBtnActive }"
                data-test-id="templateEdit_form_saveCanvas"
                @click.stop="onRelease">
                {{$t('发布')}}
            </bk-button>
        </template>
        <bk-dropdown-menu :align="'right'" ext-cls="tpl-header-more-dropdown">
            <div slot="dropdown-trigger" class="dropdown-trigger">
                <i class="bk-icon icon-more"></i>
            </div>
            <ul class="bk-dropdown-list" slot="dropdown-content">
                <li v-if="type === 'view'" class="dropdown-item" @click="$emit('onChangePanel', 'templateDataEditTab')">
                    <i class="common-icon-square-code"></i>
                    {{ 'Code' }}
                </li>
                <li v-else class="dropdown-item">{{ '废弃草稿' }}</li>
            </ul>
        </bk-dropdown-menu>

        <SelectProjectModal
            :title="$t('创建任务')"
            :show="isSelectProjectShow"
            :confirm-loading="commonTplCreateTaskPermLoading"
            :confirm-cursor="!hasCommonTplCreateTaskPerm"
            @onChange="handleProjectChange"
            @onConfirm="handleCreateTaskConfirm"
            @onCancel="handleCreateTaskCancel">
        </SelectProjectModal>
    </div>
</template>

<script>
    import { mapState, mapActions } from 'vuex'
    import permission from '@/mixins/permission.js'
    import SelectProjectModal from '@/components/common/modal/SelectProjectModal.vue'
    export default {
        name: 'TemplateHeaderRight',
        components: {
            SelectProjectModal
        },
        mixins: [permission],
        props: {
            type: String,
            name: String,
            template_id: [String, Number],
            project_id: [String, Number],
            common: String,
            templateSaving: Boolean,
            tplActions: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                isSelectProjectShow: false, // 是否显示项目选择弹窗
                editBtnActive: false, // 编辑按钮是否激活
                saveBtnActive: false, // 保存按钮是否激活.
                saveAndCreate: true, // 是否为保存并新建
                createTaskBtnActive: false, // 新建任务按钮是否激活
                hasCreateCommonTplPerm: false, // 创建公共流程权限
                hasCommonTplCreateTaskPerm: false, // 公共流程在项目下创建任务权限
                createCommonTplPermLoading: false,
                commonTplCreateTaskPermLoading: false,
                selectedProject: {} // 公共流程创建任务所选择的项目
            }
        },
        computed: {
            ...mapState({
                'permissionMeta': state => state.permissionMeta
            }),
            ...mapState('project', {
                'authActions': state => state.authActions,
                'projectName': state => state.projectName
            }),
            isViewMode () {
                return this.type === 'view'
            },
            isProjectCommonTemp () {
                const { name } = this.$route
                return name === 'projectCommonTemplatePanel'
            },
            saveRequiredPerm () {
                if (['new', 'clone'].includes(this.type)) {
                    return this.common ? ['common_flow_create'] : ['flow_create'] // 新建、克隆流程保存按钮对公共流程和普通流程的权限要求
                } else {
                    return this.common ? ['common_flow_edit'] : ['flow_edit']
                }
            }
        },
        watch: {
            
        },
        async mounted () {
            this.setEditBtnPerm()
            this.setSaveBtnPerm()
            this.setCreateTaskBtnPerm()
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            setEditBtnPerm () {
                const actions = [...this.authActions, ...this.tplActions]
                const editRequirePerm = this.common ? ['common_flow_edit'] : ['flow_edit']
                this.editBtnActive = this.hasPermission(editRequirePerm, actions)
            },
            setSaveBtnPerm () {
                const actions = [...this.authActions, ...this.tplActions]
                this.saveBtnActive = this.hasPermission(this.saveRequiredPerm, actions)
            },
            setCreateTaskBtnPerm () {
                const actions = [...this.authActions, ...this.tplActions]
                const requiredPerm = this.common ? [] : ['flow_create_task']
                this.createTaskBtnActive = this.hasPermission(requiredPerm, actions)
            },
            // 编辑流程
            onEditClick () {
                const curPermission = [...this.authActions, ...this.tplActions]
                const applyPermission = this.common ? ['common_flow_edit'] : ['flow_edit']
                if (!this.hasPermission(applyPermission, curPermission)) {
                    const permissionData = {
                        project: [{
                            id: this.project_id,
                            name: this.projectName
                        }]
                    }
                    permissionData[this.common ? 'common_flow' : 'flow'] = [{
                        id: this.template_id,
                        name: this.name
                    }]
                    this.applyForPermission(applyPermission, curPermission, permissionData)
                    return
                }
                const { params, query, name } = this.$route
                this.$router.push({
                    name,
                    params: { ...params, type: 'edit' },
                    query
                })
            },
            // 新建任务
            onCreateTask () {
                if (this.createTaskBtnActive) {
                    // 普通任务直接走模板校验、创建逻辑，公共流程先走模板校验，然后选择项目，再进行创建
                    this.$validator.validateAll().then((result) => {
                        if (!result) return
                        if (this.common) {
                            this.isSelectProjectShow = true
                        } else {
                            this.goTaskCreate(this.project_id)
                        }
                    })
                } else {
                    const requiredPerm = this.common ? ['common_flow_create'] : ['flow_create']
                    this.applyTplPerm(requiredPerm)
                }
            },
            handleProjectChange (project) {
                this.selectedProject = project
                // 查询是否有公共流程创建任务权限
                this.queryCommonTplCreateTaskPerm()
            },
            // 公共流程选择业务创建任务
            handleCreateTaskConfirm () {
                if (this.hasCommonTplCreateTaskPerm) {
                    const pid = this.selectedProject.id
                    this.goTaskCreate(pid)
                } else {
                    this.applyCommonTplCreateTaskPerm()
                }
            },
            handleCreateTaskCancel () {
                this.selectedProject = {}
                this.isSelectProjectShow = false
            },
            // 查询公共流程在项目下的创建任务权限
            async queryCommonTplCreateTaskPerm () {
                try {
                    this.commonTplCreateTaskPermLoading = true
                    const bkSops = this.permissionMeta.system.find(item => item.id === 'bk_sops')
                    const res = await this.queryUserPermission({
                        action: 'common_flow_create_task',
                        resources: [
                            {
                                system: bkSops.id,
                                type: 'project',
                                id: this.selectedProject.id,
                                attributes: {}
                            },
                            {
                                system: bkSops.id,
                                type: 'common_flow',
                                id: this.template_id,
                                attributes: {}
                            }
                        ]
                    })
                    this.hasCommonTplCreateTaskPerm = res.data.is_allow
                } catch (e) {
                    console.log(e)
                } finally {
                    this.commonTplCreateTaskPermLoading = false
                }
            },
            // 申请公共流程创建任务权限
            applyCommonTplCreateTaskPerm () {
                const curPermission = [...this.tplActions, ...this.selectedProject.auth_actions]
                const resourceData = {
                    common_flow: [{
                        id: this.template_id,
                        name: this.name
                    }],
                    project: [{
                        id: this.selectedProject.id,
                        name: this.selectedProject.name
                    }]
                }
                this.applyForPermission(['common_flow_create_task'], curPermission, resourceData)
            },
            // 跳转任务创建页
            goTaskCreate (pid) {
                this.$router.push({
                    name: 'taskCreate',
                    params: { step: 'selectnode', project_id: pid },
                    query: {
                        template_id: this.template_id,
                        common: this.common || undefined,
                        entrance: this.isViewMode ? 'templateView' : 'templateEdit',
                        fromName: this.$route.name
                    }
                })
            },
            // 发布草稿
            onRelease () {
                if (this.saveBtnActive) {
                    this.$validator.validateAll().then((result) => {
                        if (!result) return
                        this.$emit('onSaveTemplate')
                    })
                } else {
                    this.applyTplPerm(this.saveRequiredPerm)
                }
            },
            // 申请流程模板创建或编辑权限
            applyTplPerm (requiredPerm) {
                let curPermission = [...this.authActions]
                const resourceData = {}
                if (this.common) {
                    if (['view', 'edit'].includes(this.type)) { // 公共流程编辑权限
                        curPermission = [...this.tplActions]
                        resourceData.common_flow = [{
                            id: this.template_id,
                            name: this.name
                        }]
                    }
                } else {
                    resourceData.project = [{
                        id: this.project_id,
                        name: this.projectName
                    }]
                    if (['view', 'edit'].includes(this.type)) { // 普通流程编辑权限
                        curPermission = [...this.tplActions]
                        resourceData.flow = [{
                            id: this.template_id,
                            name: this.name
                        }]
                    }
                }
                this.applyForPermission(requiredPerm, curPermission, resourceData)
            }
        }
    }
</script>

<style lang="scss" scoped>
    .header-right {
        display: flex;
        align-items: center;
        .tab-operate {
            display: flex;
            align-items: center;
            position: relative;
            font-size: 14px;
            line-height: 22px;
            margin-right: 33px;
            color: #63656e;
            cursor: pointer;
            i {
                font-size: 12px;
                color: #979ba5;
                margin: 1px 6px 0 0;
            }
            &:hover {
                color: #3a84ff;
                i {
                    color: #3a84ff;
                }
            }
            &::after {
                content: '';
                display: block;
                position: absolute;
                top: 3px;
                right: -16px;
                width: 1px;
                height: 16px;
                background: #dcdee5;
            }
            &:nth-of-type(3){
                margin-right: 24px;
                &::after {
                    display: none;
                }
            }
        }
        .create-btn,
        .release-btn {
            margin-left: 8px;
        }
        .recently-text {
            font-size: 12px;
            color: #979ba5;
            margin-right: 16px;
        }
        .tpl-header-more-dropdown {
            .dropdown-trigger {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 20px;
                height: 20px;
                margin-left: 14px;
                font-size: 16px;
                color: #979ba5;
                background: transparent;
                border-radius: 50%;
                cursor: pointer;
                &:hover {
                    color: #3a84ff;
                    background: #eaebf0;
                }
            }
            .dropdown-item {
                display: flex;
                align-items: center;
                width: 90px;
                height: 32px;
                padding-left: 12px;
                font-size: 12px;
                color: #63656e;
                cursor: pointer;
                i {
                    color: #979ba5;
                    font-size: 14px;
                    margin-right: 4px;
                }
                &:hover {
                    background: #f5f7fa;
                    color: #3a84ff;
                    i {
                        color: #3a84ff;
                    }
                }
            }
        }
    }
</style>
