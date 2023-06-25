<template>
    <div class="task-scheme" v-if="isSchemeShow">
        <div class="scheme-nav" @click="toggleSchemePanel">
            <i class="bk-icon icon-angle-left"></i>
            <span>{{ $t('执行方案') }}</span>
        </div>
        <div class="scheme-list-panel" v-if="showPanel">
            <div class="scheme-sideslider-header">
                <span>{{$t('执行方案')}}</span>
                <i @click="toggleSchemePanel" class="bk-icon icon-close-line"></i>
            </div>
            <div class="scheme-active-wrapper" v-if="!isPreviewMode">
                <div>
                    <bk-button data-test-id="createTask_form_createScheme" icon="plus-line" @click="onCreateScheme">{{ $t('新增') }}</bk-button>
                    <bk-button data-test-id="createTask_form_importTemporaryPlan" @click="onImportTemporaryPlan">{{ $t('导入临时方案') }}</bk-button>
                </div>
                <bk-button data-test-id="createTask_form_togglePreview" @click="onChangePreviewNode">{{ isPreview ? $t('关闭预览') : $t('节点预览')}}</bk-button>
            </div>
            <div class="scheme-content" data-test-id="createTask_form_schemeList">
                <p :class="['scheme-title', { 'data-empty': !schemeList.length && !nameEditing }]">
                    <bk-checkbox
                        :value="isAllChecked"
                        :indeterminate="indeterminate"
                        :disabled="!schemeList.length"
                        @change="onAllCheckChange">
                    </bk-checkbox>
                    <span class="scheme-name">{{ $t('方案名称') }}</span>
                </p>
                <ul class="scheme-list" v-if="schemeList.length || nameEditing">
                    <li class="add-scheme" :class="{ 'vee-errors': veeErrors.has('schemeName'), 'is-mepty': !schemeList.length }" v-if="nameEditing">
                        <bk-input
                            ref="nameInput"
                            v-model="schemeName"
                            v-validate.persist="schemeNameRule"
                            name="schemeName"
                            class="bk-input-inline"
                            :clearable="true"
                            @blur="handlerBlur"
                            @keyup.enter.native="onAddScheme"
                            :placeholder="$t('方案名称')">
                        </bk-input>
                        <p class="common-error-tip error-msg">
                            {{ veeErrors.first('schemeName') }}
                        </p>
                    </li>
                    <li
                        v-for="item in schemeList"
                        class="scheme-item"
                        :class="{ 'is-checked': Boolean(planDataObj[item.uuid]) }"
                        :key="item.uuid">
                        <bk-checkbox
                            :value="Boolean(planDataObj[item.uuid])"
                            @change="onCheckChange($event, item)">
                        </bk-checkbox>
                        <span class="scheme-name" :title="item.name">{{item.name}}</span>
                        <span v-if="item.isDefault" class="default-label">{{$t('默认')}}</span>
                        <i
                            v-if="isSchemeEditable"
                            class="bk-icon icon-close-circle-shape"
                            @click.stop="onDeleteScheme(item)">
                        </i>
                    </li>
                </ul>
                <!-- 无数据提示 -->
                <NoData v-else></NoData>
            </div>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import permission from '@/mixins/permission.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'TaskScheme',
        components: {
            NoData
        },
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
            tplActions: {
                type: Array,
                default () {
                    return []
                }
            },
            planDataObj: {
                type: Object,
                default: () => {}
            }
        },
        data () {
            return {
                showPanel: true,
                nameEditing: false,
                schemeName: '',
                schemeNameRule: {
                    required: true,
                    max: STRING_LENGTH.SCHEME_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                schemeList: [],
                defaultIdList: [],
                defaultSchemeId: null,
                deleting: false,
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
                return selectPlanLength && selectPlanLength === this.schemeList.length
            },
            indeterminate () {
                const selectPlanLength = Object.keys(this.planDataObj).length
                return Boolean(selectPlanLength) && selectPlanLength !== this.schemeList.length
            }
        },
        watch: {
            isPreviewMode (val) {
                this.isPreview = val
            }
        },
        created () {
            this.initLoad()
        },
        methods: {
            ...mapActions('task/', [
                'loadTaskScheme',
                'createTaskScheme',
                'deleteTaskScheme',
                'getDefaultTaskScheme',
                'updateDefaultScheme'
            ]),
            // 选择方案并进行切换更新选择的节点
            onCheckChange (e, scheme) {
                this.$emit('selectScheme', scheme, e)
            },
            async initLoad () {
                try {
                    await this.loadDefaultSchemeList()
                    this.loadSchemeList()
                } catch (error) {
                    console.warn(error)
                }
            },
            // 获取方案列表
            async loadSchemeList () {
                try {
                    this.schemeList = await this.loadTaskScheme({
                        project_id: this.project_id,
                        template_id: this.template_id,
                        isCommon: this.isCommonProcess
                    }) || []
                    const defaultObj = {}
                    this.schemeList.forEach(scheme => {
                        this.$set(scheme, 'isDefault', false)
                        this.$set(scheme, 'uuid', scheme.id)
                        if (this.defaultIdList.includes(scheme.uuid)) {
                            scheme.isDefault = true
                            defaultObj[scheme.uuid] = JSON.parse(scheme.data)
                        }
                    })
                    this.$emit('updateTaskSchemeList', this.schemeList, false)
                    this.$emit('setDefaultScheme', defaultObj)
                    this.$emit('setDefaultSelected', false)
                } catch (e) {
                    console.log(e)
                }
            },
            // 获取默认方案列表
            async loadDefaultSchemeList () {
                try {
                    const resp = await this.getDefaultTaskScheme({
                        project_id: this.isCommonProcess ? undefined : this.project_id,
                        template_type: this.isCommonProcess ? 'common' : undefined,
                        template_id: Number(this.template_id)
                    })
                    if (resp.data.length) {
                        const { id, scheme_ids: schemeIds } = resp.data[0]
                        this.defaultSchemeId = id
                        this.defaultIdList = schemeIds
                    }
                } catch (error) {
                    console.warn(error)
                }
            },
            /**
             * 更新默认方案
            */
            async onSaveDefaultExecuteScheme () {
                try {
                    const ids = this.schemeList.reduce((acc, cur) => {
                        if (cur.isDefault) {
                            acc.push(cur.uuid)
                        }
                        return acc
                    }, [])
                    const params = {
                        project_id: this.isCommonProcess ? undefined : this.project_id,
                        template_type: this.isCommonProcess ? 'common' : undefined,
                        template_id: Number(this.template_id),
                        scheme_ids: ids,
                        id: this.defaultSchemeId
                    }
                    await this.updateDefaultScheme(params)
                } catch (error) {
                    console.warn(error)
                }
            },
            /**
             * 执行方案全选/半选
             */
            onAllCheckChange (val) {
                this.$emit('selectAllScheme', val)
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
                this.$emit('onImportTemporaryPlan')
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
            /**
             * 添加方案输入框失焦事件
             */
            handlerBlur () {
                this.nameEditing = this.schemeName.trim() !== ''
                if (!this.nameEditing) {
                    this.veeErrors.clear()
                }
            },
            /**
             * 添加方案
             */
            onAddScheme () {
                if (this.schemeName === '') {
                    this.nameEditing = false
                    return
                }

                const isschemeNameExist = this.schemeList.some(item => item.name === this.schemeName)
                if (isschemeNameExist) {
                    this.$bkMessage({
                        message: i18n.t('方案名称已存在'),
                        theme: 'error',
                        delay: 10000
                    })
                    return
                }
                this.$validator.validateAll().then(async (result) => {
                    if (!result) {
                        this.schemeName = ''
                        this.nameEditing = false
                        return
                    }
                    this.schemeName = this.schemeName.trim()
                    const selectedNodes = this.selectedNodes.slice()
                    const scheme = {
                        project_id: this.project_id,
                        template_id: this.template_id,
                        name: this.schemeName,
                        data: JSON.stringify(selectedNodes),
                        isCommon: this.isCommonProcess
                    }
                    try {
                        const resp = await this.createTaskScheme(scheme)
                        resp.data.uuid = resp.data.id
                        this.schemeList.push(resp.data)
                        this.$bkMessage({
                            message: i18n.t('新增方案成功'),
                            theme: 'success'
                        })
                        this.$emit('updateTaskSchemeList', this.schemeList, true)
                    } catch (e) {
                        console.log(e)
                    } finally {
                        this.schemeName = ''
                        this.nameEditing = false
                    }
                })
            },
            /**
             * 删除方案
             */
            async onDeleteScheme (scheme) {
                const tplAction = this.isCommonProcess ? 'common_flow_edit' : 'flow_edit'
                const hasPermission = this.checkSchemeRelativePermission([tplAction])

                if (this.deleting || !hasPermission) return
                this.deleting = true
                try {
                    await this.deleteTaskScheme({ id: scheme.uuid, isCommon: this.isCommonProcess })
                    if (scheme.isDefault) {
                        scheme.isDefault = false
                        await this.onSaveDefaultExecuteScheme()
                    }
                    const index = this.schemeList.findIndex(item => item.uuid === scheme.uuid)
                    this.schemeList.splice(index, 1)
                    this.onCheckChange(false, scheme)
                    this.$bkMessage({
                        message: i18n.t('方案删除成功'),
                        theme: 'success'
                    })
                    this.$emit('updateTaskSchemeList', this.schemeList, true)
                } catch (e) {
                    console.log(e)
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
    .scheme-list-panel {
        position: absolute;
        top: 0;
        right: 0;
        width: 640px;
        height: 100%;
        padding: 0 24px;
        display: flex;
        flex-direction: column;
        background: $whiteDefault;
        border-left: 1px solid $commonBorderColor;
        box-shadow: 0 0 8px rgba(0, 0, 0, 0.15);
        z-index: 5;
        transition: right 0.5s ease-in-out;
        .scheme-sideslider-header {
            height: 54px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 16px;
            color: #313238;
            .icon-close-line {
                color: #63656e;
                font-size: 14px;
                font-weight: 600;
                margin-right: 3px;
                cursor: pointer;
                &:hover {
                    color: #3a84ff;
                }
            }
        }
        .scheme-active-wrapper {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 0px 15px;
            border-top: 1px solid #dcdee5;
            /deep/.bk-button {
                width: auto;
                margin-left: 10px;
                &:first-child {
                    width: 80px;
                    margin-left: 0;
                }
                .icon-plus-line {
                    font-size: 16px;
                    margin-right: 3px;
                    color: #979ba5;
                }
            }
        }
        .add-scheme {
            position: relative;
            padding: 4px 0 5px 16px;
            border-bottom: 1px solid #f0f1f5;
            .bk-input-inline {
                width: 320px;
            }
            .common-error-tip {
                display: none;
            }
            &.is-mepty {
                border-bottom: none;
            }
        }
        .scheme-content {
            max-height: calc(100% - 127px);
            border: 1px solid #dee0e6;
            .scheme-title, .scheme-item {
                position: relative;
                height: 42px;
                display: flex;
                align-items: center;
                font-size: 12px;
                padding-left: 16px;
                border-bottom: 1px solid #ebebeb;
            }
            .scheme-list {
                height: calc(100% - 41px);
                overflow: hidden;
                overflow-y: auto;
                @include scrollbar;
            }
            .scheme-name {
                max-width: 400px;
                margin-left: 10px;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
                color: #313238;
            }
            .default-label {
                height: 22px;
                line-height: 22px;
                font-size: 12px;
                padding: 0 10px;
                border-radius: 2px;
                margin-left: 10px;
                color: #14a568;
                background: #e4faf0;
            }
            .icon-close-circle-shape {
                position: absolute;
                top: 15px;
                right: 10px;
                font-size: 14px;
                color: #cecece;
                opacity: 0;
                cursor: pointer;
                &:hover {
                    color: #979ba5;
                }
            }
            .scheme-item {
                &:hover {
                    background: #f0f1f5;
                    .icon-close-circle-shape {
                        opacity: 1;
                    }
                }
                &.is-checked {
                    background: #eaf3ff;
                    .icon-close-circle-shape {
                        opacity: 1;
                    }
                }
                &:last-child {
                    border-bottom: none;
                }
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
    .scheme-nav {
        position: absolute;
        right: 0;
        top: 20px;
        width: 72px;
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
<style lang="scss">
    .vee-errors {
        .bk-form-input {
            border-color: #ff5757;
        }
        .common-error-tip {
            margin-top: 5px;
            display: block !important;
        }
    }
</style>
