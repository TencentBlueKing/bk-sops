<template>
    <div class="task-scheme" v-if="isSchemeShow">
        <div class="schema-nav">
            <div class="scheme-combine-shape" @click="toggleSchemePanel">
                <i class="common-icon-paper"
                    v-bk-tooltips="{
                        content: $t('执行方案'),
                        placements: ['top']
                    }">
                </i>
            </div>
        </div>
        <div class="schema-list-panel" v-if="showPanel">
            <template v-if="!isEditSchemeShow">
                <div class="scheme-title">
                    <span> {{$t('执行方案')}}</span>
                    <div>
                        <bk-button size="small" theme="primary" @click="onChangePreviewNode">{{ isPreview ? $t('关闭预览') : $t('节点预览')}}</bk-button>
                        <bk-button size="small" @click="isEditSchemeShow = true">导入临时方案</bk-button>
                    </div>
                </div>
                <div :class="['scheme-header', { 'disabled-btn': !hasPermission(['flow_edit'], tplActions) }]">
                    <div class="scheme-form" v-if="nameEditing">
                        <bk-input
                            ref="nameInput"
                            v-model="schemaName"
                            v-validate="schemaNameRule"
                            data-vv-validate-on=" "
                            name="schemaName"
                            class="bk-input-inline"
                            :clearable="true"
                            @keyup.enter.native="onAddScheme"
                            :placeholder="$t('方案名称')">
                        </bk-input>
                        <span v-if="veeErrors.has('schemaName')" class="common-error-tip error-msg">{{ veeErrors.first('schemaName') }}</span>
                    </div>
                    <div
                        v-else
                        class="add-plan"
                        @click="onCreateScheme">
                        <span class="common-icon-add"></span>
                        {{ $t('新增方案') }}
                    </div>
                </div>
                <div :class="['scheme-content', { 'disable-scheme-list': isPreviewMode }]">
                    <ul class="schemeList">
                        <li
                            v-for="item in schemaList"
                            class="scheme-item"
                            :key="item.id">
                            <bk-checkbox @change="onCheckChange($event, item)"></bk-checkbox>
                            <span class="scheme-name" :title="item.name">{{item.name}}</span>
                            <i v-if="isSchemeEditable" class="bk-icon icon-close-circle-shape" @click.stop="onDeleteScheme(item)"></i>
                        </li>
                    </ul>
                </div>
            </template>
            <bk-sideslider
                v-else
                :is-show="isEditSchemeShow"
                :width="800"
                :quick-close="false"
                :before-close="onCloseEditScheme">
                <div slot="header">
                    <span class="title-back" @click="onCloseEditScheme">{{$t('执行方案')}}</span>
                    >
                    <span>{{ $t('导入临时方案') }}</span>
                </div>
                <edit-scheme
                    slot="content"
                    :is-show.sync="isEditSchemeShow"
                    :ordered-node-data="orderedNodeData"
                    @importTextScheme="$emit('importTextScheme', $event)">
                </edit-scheme>
            </bk-sideslider>
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
    import EditScheme from './EditScheme.vue'

    export default {
        name: 'TaskSchema',
        components: {
            EditScheme
        },
        mixins: [permission],
        props: {
            template_id: {
                type: [String, Number],
                default: ''
            },
            initTemplateId: {
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
            orderedNodeData: {
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
                deleting: false,
                isEditSchemeShow: false,
                isPreview: false
            }
        },
        computed: {
            ...mapState('project', {
                'projectId': state => state.project_id,
                'projectName': state => state.projectName
            })
        },
        watch: {
            isPreviewMode (val) {
                this.isPreview = val
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
                this.$emit('selectScheme', scheme, e)
            },
            // 获取方案列表
            async loadSchemeList () {
                try {
                    this.schemaList = await this.loadTaskScheme({
                        project_id: this.project_id,
                        template_id: this.initTemplateId || this.template_id,
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
                const hasCreatePermission = this.checkSchemeRelativePermission(['flow_edit'])
                if (hasCreatePermission && !this.isPreviewMode) {
                    this.nameEditing = true
                    this.$nextTick(() => {
                        this.$refs.nameInput.focus()
                    })
                }
            },
            /**
             * 添加方案
             */
            onAddScheme () {
                if (this.schemaName === '') {
                    this.nameEditing = false
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
                        this.nameEditing = false
                        return
                    }
                    this.schemaName = this.schemaName.trim()
                    const selectedNodes = this.selectedNodes.slice()
                    if (!this.isEditProcessPage) {
                        this.schemaList.push({
                            data: JSON.stringify(selectedNodes),
                            name: this.schemaName,
                            id: uuid()
                        })
                        this.$bkMessage({
                            message: i18n.t('方案添加成功'),
                            theme: 'success'
                        })
                        this.$emit('updateTaskSchemeList', this.schemaList)
                        this.schemaName = ''
                        this.nameEditing = false
                        return
                    }
                    const scheme = {
                        project_id: this.project_id,
                        template_id: this.template_id,
                        name: this.schemaName,
                        data: JSON.stringify(selectedNodes),
                        isCommon: this.isCommonProcess
                    }
                    try {
                        await this.createTaskScheme(scheme)
                        this.loadSchemeList()
                        this.$bkMessage({
                            message: i18n.t('方案添加成功'),
                            theme: 'success'
                        })
                    } catch (e) {
                        errorHandler(e, this)
                    } finally {
                        this.schemaName = ''
                        this.nameEditing = false
                    }
                })
            },
            /**
             * 删除方案
             */
            async onDeleteScheme (scheme) {
                const hasPermission = this.checkSchemeRelativePermission(['flow_edit'])

                if (this.deleting || !hasPermission) return
                if (!this.isEditProcessPage) {
                    const index = this.schemaList.findIndex(item => item.id === scheme.id)
                    this.schemaList.splice(index, 1)
                    this.$bkMessage({
                        message: i18n.t('方案删除成功'),
                        theme: 'success'
                    })
                    this.$emit('updateTaskSchemeList', this.schemaList)
                    return
                }
                this.deleting = true
                try {
                    await this.deleteTaskScheme({ id: scheme.id, isCommon: this.isCommonProcess })
                    this.loadSchemeList()
                    this.$bkMessage({
                        message: i18n.t('方案删除成功'),
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
                if (!this.hasPermission(required, this.tplActions)) {
                    const resourceData = {
                        flow: [{
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
            // 取消添加执行方案
            onCancel () {
                this.schemeName = ''
                this.nameEditing = false
            },
            /**
             * 预览模式的点击事件
             * @params {Boolean} isPreview  是否是预览模式
             */
            onChangePreviewNode () {
                this.isPreview = !this.isPreview
                this.$emit('togglePreviewMode', this.isPreview)
            },
            onCloseEditScheme () {
                this.isEditSchemeShow = false
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
    .title-back {
        color: #3a84ff;
        cursor: pointer;
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
        z-index: 5;
        transition: right 0.5s ease-in-out;
        .scheme-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 35px;
            margin: 20px 20px 0;
            padding-bottom: 10px;
            border-bottom: 1px solid #cacecb;
        }
        .scheme-header {
            position: relative;
            font-size: 14px;
            margin: 0px 20px;
            padding-top: 3px;
            border-bottom: 1px solid #ebebeb;
            .scheme-form {
                margin-bottom: 4px;
                position: relative;
                display: flex;
                align-items: center;
                .bk-input-inline {
                    margin-right: 10px;
                }
                .bk-form-input {
                    width: 200px;
                }
            }
            .add-plan {
                margin: 7px 0 10px 0;
                width: 100%;
                cursor: pointer;
                .common-icon-add {
                    font-size: 18px;
                    color: #3a84ff;
                    margin-right: 3px;
                }
            }
            .base-input {
                height: 32px;
                line-height: 32px;
                padding-bottom: 2px;
            }
        }
        .disabled-btn {
            &:after {
                content: '';
                position: absolute;
                left: 0;
                top: 0px;
                width: 100%;
                height: 100%;
                opacity: 0.4;
                background-color: #e1e4e8;
            }
        }
        .scheme-content {
            height: calc(100% - 127px);
            overflow: hidden;
            overflow-y: auto;
            @include scrollbar;
            .scheme-item {
                position: relative;
                margin: 0 20px;
                height: 42px;
                font-weight: 400;
                display: flex;
                align-items: center;
                font-size: 14px;
                cursor: pointer;
                border-bottom: 1px solid #ebebeb;
                &:hover {
                    margin: 0;
                    padding: 0 20px;
                    background-color: #d9e8f8;
                    .icon-close-circle-shape {
                        opacity: 1;
                        right: 25px;
                    }
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
                .icon-close-circle-shape {
                    position: absolute;
                    top: 15px;
                    right: 5px;
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
        }
        .disable-scheme-list {
            &:after {
                content: '';
                position: absolute;
                top: 55px;
                left: 0;
                width: 100%;
                height: 100%;
                opacity: 0.3;
                background-color: #e1e4e8;
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
