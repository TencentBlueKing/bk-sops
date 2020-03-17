<template>
    <div class="task-scheme" v-if="isSchemeShow">
        <div class="schema-nav">
            <div class="scheme-combine-shape" @click="toggleSchemePanel">
                <i class="common-icon-paper"
                    v-bk-tooltips="{
                        content: i18n.scheme,
                        placements: ['top']
                    }">
                </i>
            </div>
        </div>
        <div class="schema-list-panel" v-if="showPanel">
            <div class="scheme-title">
                <span> {{i18n.schemeList}}</span>
            </div>
            <div class="scheme-header">
                <div class="scheme-form" v-if="nameEditing">
                    <bk-input
                        v-model="schemaName"
                        v-validate="schemaNameRule"
                        data-vv-validate-on=" "
                        name="schemaName"
                        class="bk-input-inline"
                        :clearable="true"
                        :placeholder="i18n.schemaName">
                    </bk-input>
                    <bk-button theme="success" @click="onAddScheme">{{i18n.confirm}}</bk-button>
                    <bk-button @click="onCancel">{{i18n.cancel}}</bk-button>
                    <span v-if="errors.has('schemaName')" class="common-error-tip error-msg">{{ errors.first('schemaName') }}</span>
                </div>
                <bk-button
                    v-else
                    theme="primary"
                    :class="['save-scheme-btn', {
                        'disabled-btn': isPreviewMode,
                        'btn-permission-disable': !hasPermission(['create_scheme'], tplActions, tplOperations)
                    }]"
                    :loading="submiting"
                    v-cursor="{ active: !hasPermission(['create_scheme'], tplActions, tplOperations) }"
                    @click="onCreateScheme">
                    {{ i18n.createScheme }}
                </bk-button>
            </div>
            <div class="scheme-content">
                <ul class="schemeList">
                    <li
                        v-for="item in schemaList"
                        :class="['scheme-item', { 'selected': item.id === selectedScheme }]"
                        :key="item.id"
                        @click="onSelectScheme(item.id)">
                        <span class="scheme-name" :title="item.name">{{item.name}}</span>
                        <i v-if="isSchemeEditable" class="bk-icon icon-close-circle-shape" @click.stop="onDeleteScheme(item.id)"></i>
                    </li>
                </ul>
            </div>
            <div class="scheme-preview-mode" v-if="isSchemeEditable">
                <div class="scheme-header-division-line scheme-header-division-line-last"></div>
                <div class="preview-mode-switcher">
                    <span>
                        {{i18n.previewMode}}
                    </span>
                    <bk-switcher size="small" :value="isPreviewMode" @change="onChangePreviewNode"></bk-switcher>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import permission from '@/mixins/permission.js'

    export default {
        name: 'TaskSchema',
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
            isSchemeEditable: {
                type: Boolean,
                default: false
            },
            isPreviewMode: {
                type: Boolean,
                default: false
            },
            selectedNodes: {
                type: Array,
                default () {
                    return []
                }
            },
            tplActions: {
                type: Array,
                default () {
                    return []
                }
            },
            tplOperations: {
                type: Array,
                default () {
                    return []
                }
            },
            tplResource: {
                type: Object,
                default () {
                    return {}
                }
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
                schemaList: [],
                selectedScheme: undefined,
                submiting: false,
                deleting: false,
                i18n: {
                    schemeList: gettext('执行方案列表'),
                    createScheme: gettext('新建'),
                    confirm: gettext('保存'),
                    cancel: gettext('取消'),
                    schemaName: gettext('方案名称'),
                    previewMode: gettext('预览模式：'),
                    scheme: gettext('执行方案')
                }
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
            async loadSchemeList () {
                try {
                    this.schemaList = await this.loadTaskScheme({
                        project__id: this.project_id,
                        template_id: this.template_id,
                        isCommon: this.isCommonProcess
                    })
                } catch (error) {
                    errorHandler(error, this)
                }
            },
            /**
             * 任务方案面板是否显示
             */
            toggleSchemePanel () {
                this.showPanel = !this.showPanel
            },
            /**
             * 创建任务方案弹窗
             */
            onCreateScheme () {
                const hasCreatePermission = this.checkSchemeRelativePermission(['create_scheme'])
                if (hasCreatePermission && !this.isPreviewMode) {
                    this.nameEditing = true
                }
            },
            /**
             * 添加方案
             */
            onAddScheme () {
                if (this.submiting) return
                const isschemaNameExist = this.schemaList.some(item => item.name === this.schemaName)
                if (isschemaNameExist) {
                    errorHandler({ message: gettext('方案名称已存在') }, this)
                    return
                }
                this.submiting = true
                this.$validator.validateAll().then(async (result) => {
                    if (!result) {
                        this.submiting = false
                        return
                    }
                    this.schemaName = this.schemaName.trim()
                    const selectedNodes = this.selectedNodes.slice()
                    const scheme = {
                        project_id: this.project_id,
                        template_id: this.template_id,
                        name: this.schemaName,
                        data: JSON.stringify(selectedNodes),
                        isCommon: this.isCommonProcess
                    }
                    try {
                        const newScheme = await this.createTaskScheme(scheme)
                        this.selectedScheme = newScheme.id
                        this.schemaName = ''
                        this.nameEditing = false
                        this.loadSchemeList()
                        this.$bkMessage({
                            message: gettext('方案添加成功'),
                            theme: 'success'
                        })
                    } catch (e) {
                        errorHandler(e, this)
                    } finally {
                        this.submiting = false
                    }
                })
            },
            /**
             * 选择方案并进行切换更新选择的节点
             */
            async onSelectScheme (id) {
                let selectedScheme
                if (this.selectedScheme !== id) {
                    selectedScheme = id
                }
                this.selectedScheme = selectedScheme
                this.$emit('selectScheme', selectedScheme)
            },
            /**
             * 删除方案
             */
            async onDeleteScheme (id) {
                const hasPermission = this.checkSchemeRelativePermission(['delete_scheme'])

                if (this.deleting || !hasPermission) return
                this.deleting = true
                try {
                    await this.deleteTaskScheme({ id: id, isCommon: this.isCommonProcess })
                    this.loadSchemeList()
                    this.$bkMessage({
                        message: gettext('方案删除成功'),
                        theme: 'success'
                    })
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.deleting = false
                }
            },
            /**
             * 校验权限，若无权限弹出权限申请弹窗
             * @params {Array} required 被校验的权限
             */
            checkSchemeRelativePermission (required) {
                if (!this.hasPermission(required, this.tplActions, this.tplOperations)) {
                    const resourceData = {
                        name: this.templateName,
                        id: this.template_id,
                        auth_actions: this.tplActions
                    }
                    this.applyForPermission(required, resourceData, this.tplOperations, this.tplResource)
                    return false
                }
                return true
            },
            // 取消添加执行方案
            onCancel () {
                this.schemeName = ''
                this.nameEditing = false
            },
            /**
             * 预览模式的点击事件
             * @params {Boolean} isPreview  是否是预览模式
             */
            onChangePreviewNode (isPreview) {
                this.$emit('togglePreviewMode', isPreview)
            }
        }
    }
</script>>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    @import '@/scss/config.scss';

    .task-scheme {
        position: absolute;
        top: 0;
        right: 0;
        height: 100%;
    }

    .schema-list-panel {
        position: absolute;
        top: 0;
        right: 56px;
        width: 420px;
        height: 100%;
        background: $whiteDefault;
        border-left: 1px solid $commonBorderColor;
        box-shadow: 0 0 8px rgba(0, 0, 0, 0.15);
        z-index: 4;
        transition: right 0.5s ease-in-out;
        .scheme-title {
            height: 35px;
            margin: 20px;
            border-bottom: 1px solid #cacecb;
        }
        .scheme-header {
            margin: 20px;
            .scheme-form {
                position: relative;
                display: inline-block;
                input {
                    width: 200px;
                }
                .error-msg {
                    position: absolute;
                    left: 0px;
                    bottom: -16px;
                }
            }
            .save-scheme-btn {
                width: 90px;
                height: 32px;
                line-height: 32px;
                background-color: #ffffff;
                border: 1px solid #c4c6cc;
                border-radius: 2px;
                color: #313238;
                font-size: 14px;
                font-weight: 400;
            }
            .disabled-btn {
                opacity: 0.3;
                cursor: not-allowed;
            }
            .base-input {
                height: 32px;
                line-height: 32px;
                padding-bottom: 2px;
            }
        }
        .scheme-content {
            height: calc(100% - 127px- 63px);
            overflow: hidden;
            overflow-y: auto;
            @include scrollbar;
            .scheme-item {
                margin: 0 20px;
                height: 42px;
                font-weight: 400;
                line-height: 42px;
                font-size: 14px;
                cursor: pointer;
                border-bottom: 1px solid #ebebeb;
                &:hover {
                    margin: 0;
                    padding: 0 20px;
                    background-color: #d9e8f8;
                    .icon-close-circle-shape {
                        opacity: 1;
                    }
                }
                &.selected {
                    margin: -1px 0 0 0;
                    padding: 0 20px;
                    background-color: #3a84ff;
                    .scheme-name {
                        color: #ffffff;
                    }
                    .scheme-division-line {
                        background-color: #3a84ff;
                    }
                    .icon-close-circle-shape {
                        color: #ffffff;
                        opacity: 1;
                    }
                }
                .scheme-name {
                    display: inline-block;
                    width: 240px;
                    overflow: hidden;
                    white-space: nowrap;
                    text-overflow: ellipsis;
                    color: #313238;
                }
                .icon-close-circle-shape {
                    float: right;
                    margin-top: 15px;
                    margin-right: 5px;
                    width: 12px;
                    height: 12px;
                    text-align: center;
                    line-height: 12px;
                    color: #cecece;
                    opacity: 0;
                    cursor: pointer;
                    &:hover {
                        color: #979ba5;
                    }
                }
            }
            li:first-child {
                border-top: 1px solid $commonBorderColor;
            }
        }
        .scheme-preview-mode {
            position: relative;
            width: 420px;
            .scheme-header-division-line-last {
                margin: 0 25px 0 20px;
                border: 0;
                height: 1px;
                background-color:#cacedb;
            }
            .preview-mode-switcher {
                position: relative;
                top: 19px;
                left: 20px;
                span {
                    font-size: 14px;
                    font-weight: 400;
                    color: #313238;
                }
            }
        }
    }
    .schema-nav {
        position: absolute;
        right: 0;
        float: right;
        width: 56px;
        background: #ffffff;
        border-left: 1px solid #cacedb;
        height: 100%;
        z-index: 5;
        .scheme-combine-shape {
            margin: 27px 0 0 12px;
            width: 32px;
            height: 32px;
            background-color: #525F77;
            border-radius:2px;
            text-align: center;
            line-height: 32px;
            cursor: pointer;
            .common-icon-paper {
                color: #ffffff;
            }
        }
    }
    .disable-item {
        cursor: not-allowed;
        &:hover {
            background: inherit ;
        }
    }
    .scheme-name-wrapper {
        padding: 10px 0;
        label {
            float: left;
            margin-top: 6px;
            width: 100px;
            text-align: right;
        }
        .scheme-name-input {
            margin: 0 35px 0 120px;
        }
    }
    .bk-input-inline {
        display: inline-block;
        width: 200px;
    }
</style>
