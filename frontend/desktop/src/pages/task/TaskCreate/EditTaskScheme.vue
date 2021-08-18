<template>
    <div class="edit-task-scheme" v-if="isSchemeShow">
        <div class="schema-nav" @click="toggleSchemePanel">
            <i class="bk-icon icon-angle-left"></i>
            {{ $t('执行方案') }}
        </div>
        <div class="schema-list-panel" v-if="showPanel">
            <div class="scheme-sideslider-header">
                <p class="close-btn" @click="toggleSchemePanel">
                    <i class="bk-icon icon-angle-right"></i>
                </p>
                <p>{{$t('执行方案')}}</p>
            </div>
            <div class="scheme-active-wrapper">
                <div>
                    <bk-button :disabled="isCommonProcess" icon="plus-line" @click="onCreateScheme">{{ $t('新增') }}</bk-button>
                    <bk-button :disabled="isCommonProcess" @click="onImportTemporaryPlan">{{ $t('导入临时方案') }}</bk-button>
                </div>
                <bk-button @click="onChangePreviewNode">{{ isPreview ? $t('关闭预览') : $t('节点预览')}}</bk-button>
            </div>
            <section :class="['scheme-wrapper', { 'is-diasbled': isCommonProcess }]" v-bkloading="{ isLoading: isSchemeLoading }">
                <p :class="['scheme-title', { 'data-empty': !schemaList.length && !nameEditing }]">
                    <bk-checkbox
                        :value="isAllChecked"
                        :indeterminate="indeterminate"
                        v-bk-tooltips="{ content: $t('请先保存方案再执行其他操作'), boundary: 'window', disabled: !nameEditing }"
                        :disabled="!schemaList.length || nameEditing"
                        @change="onAllCheckChange">
                    </bk-checkbox>
                    <span class="scheme-name">{{ $t('方案名称') }}</span>
                </p>
                <ul class="scheme-list" v-if="schemaList.length || nameEditing">
                    <!-- 创建方案 -->
                    <li class="add-scheme" :class="{ 'vee-errors': veeErrors.has('schemaName'), 'is-mepty': !schemaList.length }" v-if="nameEditing">
                        <bk-input
                            ref="nameInput"
                            v-model="schemaName"
                            v-validate.persist="schemaNameRule"
                            name="schemaName"
                            class="bk-input-inline"
                            :clearable="true"
                            :placeholder="$t('方案名称')"
                            @keyup.enter.native="onAddScheme">
                        </bk-input>
                        <p class="icon-btn-wrapper">
                            <i
                                v-bk-tooltips="{ content: $t('新增'), boundary: 'window' }"
                                class="bk-icon icon-check-line"
                                @click="onAddScheme">
                            </i>
                            <i
                                v-bk-tooltips="{ content: $t('删除'), boundary: 'window' }"
                                class="bk-icon icon-close-line-2"
                                @click="onCancelScheme">
                            </i>
                        </p>
                        <p class="common-error-tip error-msg">{{ veeErrors.first('schemaName') }}</p>
                    </li>
                    <!-- 方案展示列表 -->
                    <li
                        v-for="item in schemaList"
                        class="scheme-item"
                        :class="{ 'is-checked': Boolean(planDataObj[item.id]) }"
                        :key="item.id">
                        <bk-checkbox
                            :value="Boolean(planDataObj[item.id])"
                            :disabled="nameEditing"
                            v-bk-tooltips="{ content: $t('请先保存方案再执行其他操作'), boundary: 'window', disabled: !nameEditing }"
                            @change="onCheckChange($event, item)">
                        </bk-checkbox>
                        <span class="scheme-name" :title="item.name">{{item.name}}</span>
                        <p class="icon-btn-wrapper">
                            <i
                                v-bk-tooltips="{ content: $t('编辑'), boundary: 'window' }"
                                class="bk-icon icon-edit-line"
                                @click="onEditSelectScheme(item)">
                            </i>
                            <i
                                v-bk-tooltips="{ content: $t('删除'), boundary: 'window' }"
                                class="bk-icon icon-delete"
                                @click="onDeleteScheme(item)">
                            </i>
                        </p>
                    </li>
                </ul>
                <!-- 无数据提示 -->
                <bk-exception
                    v-else
                    class="exception-wrap-item exception-part"
                    type="empty"
                    scene="part">
                </bk-exception>
            </section>
            <section class="scheme-footer">
                <bk-button theme="primary" :loading="executeSchemeSaving" @click="onSaveExecuteSchemeClick">{{ $t('保存') }}</bk-button>
                <bk-button @click="toggleSchemePanel">{{ $t('返回') }}</bk-button>
            </section>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { uuid } from '@/utils/uuid.js'
    import { mapState, mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import permission from '@/mixins/permission.js'
    import bus from '@/utils/bus.js'

    export default {
        name: 'EditeTaskScheme',
        mixins: [permission],
        props: {
            template_id: {
                type: [String, Number],
                default: ''
            },
            project_id: {
                type: [String, Number],
                default: ''
            },
            templateName: {
                type: String,
                default: ''
            },
            isCommonProcess: {
                type: Boolean,
                default: false
            },
            isSchemeShow: {
                type: Boolean,
                default: false
            },
            isPreviewMode: {
                type: Boolean,
                default: false
            },
            isEditProcessPage: {
                type: Boolean,
                default: true
            },
            selectedNodes: {
                type: Array,
                default () {
                    return []
                }
            },
            planDataObj: {
                type: Object,
                default: () => {}
            },
            tplActions: {
                type: Array,
                default () {
                    return []
                }
            },
            executeSchemeSaving: {
                type: Boolean,
                default: false
            },
            schemeInfo: {
                type: Object,
                default: () => {}
            }
        },
        data () {
            return {
                showPanel: true,
                nameEditing: false,
                schemaName: '',
                schemaNameRule: {
                    required: true,
                    max: STRING_LENGTH.SCHEME_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                isSchemeLoading: true,
                schemaList: [],
                isPreview: false
            }
        },
        computed: {
            ...mapState('project', {
                'projectId': state => state.project_id,
                'projectName': state => state.projectName
            }),
            haveCreateSchemeTpl () {
                const tplAction = this.isCommonProcess ? 'common_flow_edit' : 'flow_edit'
                return this.hasPermission([tplAction], this.tplActions)
            },
            isAllChecked () {
                const selectPlanLength = Object.keys(this.planDataObj).length
                return selectPlanLength && selectPlanLength === this.schemaList.length
            },
            indeterminate () {
                const selectPlanLength = Object.keys(this.planDataObj).length
                return Boolean(selectPlanLength) && selectPlanLength !== this.schemaList.length
            }
        },
        watch: {
            isPreviewMode (val) {
                this.isPreview = val
            },
            schemeInfo (val) {
                if (!this.schemaList.length) return
                const scheme = this.schemaList.find(item => item.id === val.id)
                scheme.data = JSON.stringify(val.data)
            }
        },
        created () {
            this.loadSchemeList()
        },
        methods: {
            ...mapActions('task/', [
                'loadTaskScheme',
                'createTaskScheme',
                'deleteTaskScheme'
            ]),
            // 选择方案并进行切换更新选择的节点
            onCheckChange (e, scheme) {
                // 提示用户先保存创建方案再进行其他操作
                if (this.setRemindUserMsg()) return
                this.$emit('selectScheme', scheme, e)
            },
            // 获取方案列表
            async loadSchemeList () {
                try {
                    this.isSchemeLoading = true
                    this.schemaList = await this.loadTaskScheme({
                        project_id: this.project_id,
                        template_id: this.template_id,
                        isCommon: this.isCommonProcess
                    }) || []
                    this.$emit('updateTaskSchemeList', this.schemaList)
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.isSchemeLoading = false
                }
            },
            /**
             * 任务方案面板是否显示
             */
            toggleSchemePanel () {
                this.showPanel = !this.showPanel
            },
            /**
             * 导入临时方案
            */
            onImportTemporaryPlan () {
                // 提示用户先保存创建方案再进行其他操作
                if (this.setRemindUserMsg()) return
                let hasCreatePermission = true
                if (!this.haveCreateSchemeTpl) {
                    const tplAction = this.isCommonProcess ? 'common_flow_edit' : 'flow_edit'
                    hasCreatePermission = this.checkSchemeRelativePermission([tplAction])
                }
                if (hasCreatePermission) {
                    this.$emit('onImportTemporaryPlan')
                }
            },
            /**
             * 执行方案全选/半选
             */
            onAllCheckChange (val) {
                // 提示用户先保存创建方案再进行其他操作
                if (this.setRemindUserMsg()) return
                this.$emit('selectAllScheme', val)
            },
            /**
             * 创建任务方案弹窗
             */
            onCreateScheme () {
                let hasCreatePermission = true
                if (!this.haveCreateSchemeTpl) {
                    const tplAction = this.isCommonProcess ? 'common_flow_edit' : 'flow_edit'
                    hasCreatePermission = this.checkSchemeRelativePermission([tplAction])
                }
                if (hasCreatePermission && !this.isPreviewMode) {
                    this.veeErrors.clear()
                    this.nameEditing = true
                    this.$nextTick(() => {
                        this.$refs.nameInput.focus()
                    })
                }
            },
            // 提示用户先保存创建方案再进行其他操作
            setRemindUserMsg () {
                if (this.nameEditing) {
                    this.$bkMessage({
                        message: i18n.t('请先保存方案再执行其他操作'),
                        theme: 'warning'
                    })
                    return true
                }
                return false
            },
            /**
             * 取消创建方案
             */
            onCancelScheme () {
                this.nameEditing = false
                this.schemaName = ''
                this.veeErrors.clear()
            },
            /**
             * 添加方案
             */
            onAddScheme () {
                if (!this.selectedNodes.length) {
                    this.$bkMessage({
                        message: i18n.t('不允许添加没有节点的执行方案'),
                        theme: 'warning'
                    })
                    return
                }
                const isschemaNameExist = this.schemaList.some(item => item.name === this.schemaName)
                if (isschemaNameExist) {
                    errorHandler({ message: i18n.t('方案名称已存在') }, this)
                    return
                }
                this.$validator.validateAll().then(async (result) => {
                    if (!result) {
                        this.schemaName = ''
                        return
                    }
                    this.schemaName = this.schemaName.trim()
                    const selectedNodes = this.selectedNodes.slice()
                    this.schemaList.unshift({
                        data: JSON.stringify(selectedNodes),
                        name: this.schemaName,
                        id: uuid()
                    })
                    this.$bkMessage({
                        message: i18n.t('新增方案成功'),
                        theme: 'success'
                    })
                    this.$emit('updateTaskSchemeList', this.schemaList, true)
                    this.schemaName = ''
                    this.nameEditing = false
                })
            },
            /**
             * 预览选择的方案
             */
            onPreviewNode () {
                this.isPreview = true
            },
            /**
             * 编辑选中的方案
             */
            onEditSelectScheme (val) {
                // 提示用户先保存创建方案再进行其他操作
                if (this.setRemindUserMsg()) return
                this.$emit('onEditScheme', val)
                bus.$emit('onEditScheme', val)
            },
            /**
             * 删除方案
             */
            async onDeleteScheme (scheme) {
                // 提示用户先保存创建方案再进行其他操作
                if (this.setRemindUserMsg()) return
                const tplAction = this.isCommonProcess ? 'common_flow_edit' : 'flow_edit'
                const hasPermission = this.checkSchemeRelativePermission([tplAction])

                if (!hasPermission) return
                const index = this.schemaList.findIndex(item => item.id === scheme.id)
                this.schemaList.splice(index, 1)
                this.$bkMessage({
                    message: i18n.t('方案删除成功'),
                    theme: 'success'
                })
                this.$emit('updateTaskSchemeList', this.schemaList, true)
            },
            /**
             * 校验权限，若无权限弹出权限申请弹窗
             * @params {Array} required 被校验的权限
             */
            checkSchemeRelativePermission (required) {
                if (!this.hasPermission(required, this.tplActions)) {
                    const flowType = this.isCommonProcess ? 'common_flow' : 'flow'
                    const resourceData = {
                        [`${flowType}`]: [{
                            id: this.template_id,
                            name: this.templateName
                        }],
                        project: [{
                            id: this.projectId,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission(required, this.tplActions, resourceData)
                    return false
                }
                return true
            },
            /**
             * 预览模式的点击事件
             * @params {Boolean} isPreview  是否是预览模式
             */
            onChangePreviewNode () {
                // 提示用户先保存创建方案再进行其他操作
                if (this.setRemindUserMsg()) return
                this.isPreview = !this.isPreview
                this.$emit('togglePreviewMode', this.isPreview)
            },
            onSaveExecuteSchemeClick () {
                this.$emit('onSaveExecuteSchemeClick')
            }
        }
    }
</script>>
<style lang="scss">
    .edit-task-scheme {
        .scheme-active-wrapper .bk-button > div {
            display: flex;
            align-items: center;
            .icon-plus-line {
                font-size: 16px;
                margin-right: 3px;
                color: #979ba5;
            }
        }
        .scheme-wrapper {
            .bk-checkbox:hover {
                border-color: #3a84ff;
            }
            .is-disabled {
                &.is-indeterminate .bk-checkbox {
                    border-color: #dcdee5;
                    background-color: #dcdee5;
                }
                &:hover .bk-checkbox {
                    border-color: #dcdee5 !important;
                }
            }
            .vee-errors {
                .bk-form-input {
                    border-color: #ff5757;
                }
                .common-error-tip {
                    margin-top: 5px;
                    display: block !important;
                }
            }
        }
    }
</style>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    @import '@/scss/config.scss';

    .edit-task-scheme {
        position: absolute;
        top: 0;
        right: 0;
        height: 100%;
    }
    .schema-list-panel {
        position: absolute;
        top: 0;
        right: 0;
        width: 486px;
        height: 100%;
        display: flex;
        flex-direction: column;
        background: $whiteDefault;
        border-left: 1px solid $commonBorderColor;
        box-shadow: 0 0 8px rgba(0, 0, 0, 0.15);
        z-index: 5;
        transition: right 0.5s ease-in-out;
        padding-bottom: 56px;
        .scheme-sideslider-header {
            height: 54px;
            font-size: 16px;
            p {
                height: 100%;
                line-height: 54px;
                border-bottom: 1px solid #dee0e6;
            }
            .close-btn {
                width: 30px;
                float: left;
                text-align: center;
                font-size: 28px;
                color: #fff;
                margin-right: 20px;
                cursor: pointer;
                background: #3a84ff;
                border-bottom-color: #3a84ff;
            }
        }
        .scheme-active-wrapper {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 20px 23px 0 16px;
            .bk-button {
                width: 80px;
                &:nth-child(2) {
                    width: auto;
                    margin-left: 10px;
                }
            }
        }
        .scheme-wrapper {
            border: 1px solid #dee0e6;
            margin: 15px 23px 15px 16px;
            max-height: calc(100% - 136px);
            .scheme-list {
                height: calc(100% - 41px);
                overflow: hidden;
                overflow-y: auto;
                @include scrollbar;
            }
            .scheme-title, .scheme-item {
                position: relative;
                height: 42px;
                display: flex;
                align-items: center;
                font-size: 12px;
                padding-left: 12px;
                border-bottom: 1px solid #ebebeb;
            }
            .scheme-name {
                display: inline-block;
                width: 240px;
                margin-left: 10px;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
                color: #313238;
            }
            .icon-btn-wrapper {
                position: absolute;
                top: 15px;
                right: 10px;
                display: flex;
                align-items: center;
                opacity: 0;
                transition: opacity .5s;
                .bk-icon {
                    font-size: 16px;
                    cursor: pointer;
                    color: #979ba5;
                    margin-left: 12px;
                    font-weight: 500;
                    &:hover {
                        color: #3a84ff !important;
                    }
                }
            }
            .scheme-title {
                background: #fafbfd;
                border-top: none;
            }
            .scheme-item {
                &:hover {
                    background-color: #f0f1f5;
                    .icon-btn-wrapper {
                        opacity: 1;
                    }
                }
                &.is-checked {
                    background: #eaf3ff;
                    .icon-btn-wrapper {
                        opacity: 1;
                    }
                }
                &:last-child {
                    border-bottom: none;
                }
            }
            .add-scheme {
                position: relative;
                padding: 5px 0 5px 12px;
                border-bottom: 1px solid #f0f1f5;
                .icon-btn-wrapper {
                    opacity: 1;
                    transform: translate(-10px, -4px);
                    .bk-icon {
                        font-size: 20px;
                        color: #63656e;
                    }
                }
                .common-error-tip {
                    display: none;
                }
                &.is-mepty {
                    border-bottom: none;
                }
            }
            .exception-part {
                margin: 55px 0;
            }
        }
        .scheme-footer {
            position: absolute;
            left: 0;
            bottom: 0;
            height: 56px;
            width: 100%;
            border-top: 1px solid #f0f1f5;
            padding-left: 16px;
            line-height: 56px;
            .bk-button {
                width: 86px;
                margin-right: 5px;
            }
        }
        .is-diasbled {
            &:after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                opacity: 0.3;
                background-color: #e1e4e8;
            }
        }
    }
    .schema-nav {
        position: absolute;
        right: 0;
        top: 20px;
        width: 72px;
        height: 24px;
        z-index: 5;
        background: #fafbfd;
        border: 1px solid #3a84ff;
        border-right: none;
        border-radius: 12px 0px 0px 12px;
        font-size: 12px;
        line-height: 22px;
        vertical-align: middle;
        color: #3a84ff;
        cursor: pointer;
        .bk-icon {
            font-size: 16px;
            position: relative;
            left: 4px;
            top: 1px;
        }
    }
    .bk-input-inline {
        display: inline-block;
        width: 320px;
    }
</style>
