<template>
    <div class="edit-task-scheme" v-if="isSchemeShow">
        <div class="scheme-nav" @click="showPanel = !showPanel">
            <i class="bk-icon icon-angle-left"></i>
            {{ $t('执行方案') }}
        </div>
        <div class="scheme-list-panel" v-if="showPanel">
            <div class="scheme-sideslider-header">
                <p>{{$t('执行方案')}}</p>
                <i class="bk-icon icon-close-line" @click="showPanel = !showPanel"></i>
            </div>
            <bk-alert type="info" class="single-use-alert">
                <template slot="title">
                    <i18n tag="div" path="editSchemeTips">
                        <span class="single-use" @click="onImportTemporaryPlan">{{ $t('导入选择') }}</span>
                    </i18n>
                </template>
            </bk-alert>
            <div class="scheme-active-wrapper">
                <bk-button
                    data-test-id="templateEdit_form_addScheme"
                    icon="plus-line"
                    :disabled="nameEditing || isSchemeEditing"
                    @click="onCreateScheme">
                    {{ $t('新增') }}
                </bk-button>
                <bk-button
                    data-test-id="templateEdit_form_previewNode"
                    :disabled="nameEditing || isSchemeEditing"
                    @click="onChangePreviewNode">
                    {{ isPreview ? $t('关闭预览') : $t('节点预览')}}
                </bk-button>
            </div>
            <section
                data-test-id="templateEdit_form_schemeList"
                class="scheme-wrapper"
                v-bkloading="{ isLoading: isSchemeLoading }">
                <p :class="['scheme-title', { 'data-empty': !schemeList.length && !nameEditing }]">
                    <bk-checkbox
                        :value="isAllChecked"
                        :indeterminate="indeterminate"
                        v-bk-tooltips="{ content: $t('请先保存方案再执行其他操作'), boundary: 'window', disabled: !nameEditing && !isSchemeEditing }"
                        :disabled="!schemeList.length || nameEditing || isSchemeEditing"
                        @change="onAllCheckChange">
                    </bk-checkbox>
                    <span class="scheme-name">{{ $t('方案名称') }}</span>
                </p>
                <ul class="scheme-list" v-if="schemeList.length || nameEditing">
                    <!-- 创建方案 -->
                    <li class="add-scheme" :class="{ 'vee-errors': veeErrors.has('schemeName'), 'is-empty': !schemeList.length }" v-if="nameEditing">
                        <bk-input
                            ref="nameInput"
                            v-model="schemeName"
                            v-validate.persist="schemeNameRule"
                            name="schemeName"
                            class="bk-input-inline"
                            :clearable="true"
                            :placeholder="$t('方案名称')"
                            @keyup.enter.native="onAddScheme">
                        </bk-input>
                        <div class="icon-btn-wrapper">
                            <i
                                v-bk-tooltips="{ content: $t('新增'), boundary: 'window' }"
                                class="bk-icon icon-check-line"
                                @click="onAddScheme">
                            </i>
                            <i
                                v-bk-tooltips="{ content: $t('取消'), boundary: 'window' }"
                                class="bk-icon icon-close-line-2"
                                @click="onCancelScheme">
                            </i>
                        </div>
                        <p class="common-error-tip error-msg">{{ veeErrors.first('schemeName') }}</p>
                    </li>
                    <!-- 方案展示列表 -->
                    <li
                        v-for="item in schemeList"
                        :class="['scheme-item', { 'is-checked': item.isChecked, 'is-edited': item.isEdit }]"
                        :key="item.id"
                        v-bkloading="{ isLoading: item.isLoading }">
                        <template v-if="item.isEdit">
                            <bk-input
                                v-model="item.name"
                                :ref="`scheme-${item.id}`"
                                v-validate.persist="schemeNameRule"
                                name="schemeName"
                                class="bk-input-inline"
                                :clearable="true"
                                :placeholder="$t('方案名称')"
                                @keyup.enter.native="onUpdateScheme(item)">
                            </bk-input>
                            <div class="icon-btn-wrapper">
                                <i
                                    v-bk-tooltips="{ content: $t('保存'), boundary: 'window' }"
                                    class="bk-icon icon-check-line"
                                    @click="onUpdateScheme(item)">
                                </i>
                                <i
                                    v-bk-tooltips="{ content: $t('取消'), boundary: 'window' }"
                                    class="bk-icon icon-close-line-2"
                                    @click="onCancelUpdateScheme(item)">
                                </i>
                            </div>
                            <p class="common-error-tip error-msg mt5">{{ veeErrors.first('schemeName') }}</p>
                        </template>
                        <template v-else>
                            <bk-checkbox
                                :value="item.isChecked"
                                :disabled="nameEditing || isSchemeEditing"
                                v-bk-tooltips="{ content: $t('请先保存方案再执行其他操作'), boundary: 'window', disabled: !nameEditing && !isSchemeEditing }"
                                @change="onCheckChange(item)">
                            </bk-checkbox>
                            <span class="scheme-name" :title="item.name">{{item.name}}</span>
                            <span v-if="item.quote_count > 0" class="quoted-count">{{ $tc('被个子流程引用', item.quote_count, { n: item.quote_count }) }}</span>
                            <div class="icon-btn-wrapper">
                                <i
                                    v-if="!isSchemeEditing && !nameEditing"
                                    v-bk-tooltips="{ content: $t('编辑'), boundary: 'window' }"
                                    class="bk-icon icon-edit-line"
                                    @click="onEditSelectScheme(item)">
                                </i>
                                <i
                                    v-if="!isSchemeEditing && !nameEditing"
                                    v-bk-tooltips="{ content: $t('删除'), boundary: 'window' }"
                                    :class="['bk-icon icon-delete', { disabled: item.quote_count > 0 }]"
                                    @click="onDeleteScheme(item)">
                                </i>
                                <i
                                    v-if="(isSchemeEditing || nameEditing) ? item.isDefault : true"
                                    v-bk-tooltips="{ content: item.isDefault ? $t('取消设为默认方案') : $t('设为默认方案'), boundary: 'window' }"
                                    :class="['common-icon-default', { 'is-default': item.isDefault }]"
                                    @click="onToggleDefaultPlan(item)">
                                </i>
                            </div>
                        </template>
                    </li>
                </ul>
                <!-- 无数据提示 -->
                <NoData v-else :message="$t('暂无方案')"></NoData>
            </section>
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
        name: 'EditTaskScheme',
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
            defaultPlanDataObj: {
                type: Object,
                default: () => {}
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
                schemeName: '',
                schemeNameRule: {
                    required: true,
                    max: STRING_LENGTH.SCHEME_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                isSchemeLoading: true,
                schemeList: [],
                defaultSchemeList: [],
                isUpdate: false,
                defaultSchemeId: null,
                isPreview: false,
                previousCheckedScheme: []
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
                return this.schemeList.length && this.schemeList.every(item => item.isChecked)
            },
            indeterminate () {
                return !this.isAllChecked && this.schemeList.some(item => item.isChecked)
            },
            isSchemeEditing () {
                return this.schemeList.some(item => item.isEdit)
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
                'updateTaskScheme',
                'deleteTaskScheme',
                'getDefaultTaskScheme',
                'saveDefaultScheme',
                'updateDefaultScheme',
                'deleteDefaultScheme'
            ]),
            // 选择方案并进行切换更新选择的节点
            onCheckChange (scheme) {
                scheme.isChecked = !scheme.isChecked
                this.$emit('selectScheme')
            },
            async initLoad () {
                try {
                    this.isSchemeLoading = true
                    await this.loadDefaultSchemeList()
                    this.loadSchemeList()
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isSchemeLoading = false
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
                    this.schemeList.forEach(scheme => {
                        this.$set(scheme, 'isEdit', false)
                        this.$set(scheme, 'isChecked', false)
                        this.$set(scheme, 'isLoading', false)
                        this.$set(scheme, 'isDefault', false)
                        if (this.defaultSchemeList.includes(scheme.id)) {
                            scheme.isDefault = true
                        }
                    })
                    // 画布按默认方案来勾选节点
                    this.$emit('setCanvasSelected', [])
                } catch (error) {
                    console.error(error)
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
                        this.isUpdate = true
                        const { id, scheme_ids: schemeIds } = resp.data[0]
                        this.defaultSchemeId = id
                        this.defaultSchemeList = schemeIds
                    } else {
                        this.isUpdate = false
                    }
                } catch (error) {
                    console.error(error)
                } finally {
                    this.isSchemeLoading = false
                }
            },
            /**
             * 临时方案
            */
            onImportTemporaryPlan () {
                // 提示用户先保存创建方案再进行其他操作
                if (this.nameEditing || this.isSchemeEditing) {
                    this.$bkMessage({
                        message: i18n.t('请先保存方案再执行其他操作'),
                        theme: 'warning'
                    })
                    return true
                }
                this.$emit('onImportTemporaryPlan')
            },
            /**
             * 设为默认方案
            */
            async onToggleDefaultPlan (scheme) {
                if (this.nameEditing || this.isSchemeEditing) return
                try {
                    scheme.isLoading = true
                    scheme.isDefault = !scheme.isDefault
                    await this.onSaveDefaultExecuteScheme()
                    this.$bkMessage({
                        message: i18n.t(scheme.isDefault ? '添加默认方案成功' : '取消默认方案成功'),
                        theme: 'success'
                    })
                } catch (error) {
                    console.warn(error)
                } finally {
                    scheme.isLoading = false
                }
            },
            /**
             * 保存/更新默认方案
            */
            async onSaveDefaultExecuteScheme () {
                try {
                    const ids = this.schemeList.reduce((acc, cur) => {
                        if (cur.isDefault) {
                            acc.push(cur.id)
                        }
                        return acc
                    }, [])
                    const params = {
                        project_id: this.isCommonProcess ? undefined : this.project_id,
                        template_id: Number(this.template_id),
                        template_type: this.isCommonProcess ? 'common' : undefined,
                        scheme_ids: ids,
                        id: this.defaultSchemeId
                    }
                    const defaultSchemeFunc = !ids.length ? this.deleteDefaultScheme : this.isUpdate ? this.updateDefaultScheme : this.saveDefaultScheme
                    const resp = await defaultSchemeFunc(params)
                    if (!ids.length) {
                        this.isUpdate = false
                    } else if (!this.isUpdate) {
                        this.isUpdate = true
                        this.defaultSchemeId = resp.data.id
                    }
                    return resp.result
                } catch (error) {
                    console.warn(error)
                }
            },
            /**
             * 执行方案全选/半选
             */
            onAllCheckChange (val) {
                this.schemeList.forEach(scheme => {
                    scheme.isChecked = val
                })
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
                    this.previousCheckedScheme = []
                    this.schemeList.forEach(item => {
                        if (item.isChecked) {
                            this.previousCheckedScheme.push(item.id)
                        }
                        item.isChecked = false
                    })
                    this.$nextTick(() => {
                        this.$refs.nameInput.focus()
                    })
                }
            },
            /**
             * 取消创建方案
             */
            onCancelScheme () {
                this.nameEditing = false
                this.schemeName = ''
                this.veeErrors.clear()
                if (this.previousCheckedScheme.length) {
                    this.schemeList.forEach(item => {
                        item.isChecked = this.previousCheckedScheme.includes(item.id)
                    })
                    this.previousCheckedScheme = []
                }
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
                const isSchemeNameExist = this.schemeList.some(item => {
                    return item.name.toLowerCase() === this.schemeName.toLowerCase()
                })
                if (isSchemeNameExist) {
                    this.$bkMessage({
                        message: i18n.t('方案名称已存在（不区分大小写）'),
                        theme: 'warning'
                    })
                    return
                }
                this.$validator.validateAll().then(async (result) => {
                    if (!result) {
                        this.schemeName = ''
                        return
                    }
                    try {
                        this.schemeName = this.schemeName.trim()
                        const selectedNodes = this.selectedNodes.slice()
                        const resp = await this.createTaskScheme({
                            isCommon: this.isCommonProcess,
                            project_id: this.project_id,
                            template_id: this.template_id,
                            data: JSON.stringify(selectedNodes),
                            name: this.schemeName
                        })
                        if (!resp.result) return
                        this.schemeList.forEach(item => {
                            item.isChecked = false
                        })
                        this.schemeList.unshift({
                            ...resp.data,
                            isEdit: false,
                            isChecked: true,
                            isLoading: false,
                            isDefault: false
                        })
                        this.$bkMessage({
                            message: i18n.t('新增方案成功'),
                            theme: 'success'
                        })
                        this.schemeName = ''
                        this.nameEditing = false
                    } catch (error) {
                        console.warn(error)
                    }
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
            onEditSelectScheme (scheme) {
                // 将当前数据记录下来
                scheme.initScheme = { ...scheme }
                // 清楚报错异常
                this.veeErrors.clear()
                scheme.isEdit = true
                // 记录编辑前选中的方案
                this.previousCheckedScheme = []
                this.previousCheckedNode = [...this.$parent.selectedNodes]
                // 将所有非当前编辑的方案改为取消选中
                this.schemeList.forEach(item => {
                    if (item.isChecked) {
                        this.previousCheckedScheme.push(item.id)
                        item.isChecked = item.id === scheme.id
                    }
                })
                // 画布按当前方案勾选节点
                this.$emit('setCanvasSelected', JSON.parse(scheme.data))
                // 获取焦点
                this.$nextTick(() => {
                    let refInstance = this.$refs[`scheme-${scheme.id}`]
                    refInstance = refInstance && refInstance[0]
                    refInstance && refInstance.focus()
                })
            },
            // 编辑方案
            async onUpdateScheme (scheme) {
                if (!this.selectedNodes.length) {
                    this.$bkMessage({
                        message: i18n.t('不允许添加没有节点的执行方案'),
                        theme: 'warning'
                    })
                    return
                }
                const isSchemeNameExist = this.schemeList.some(item => {
                    return item.name.toLowerCase() === scheme.name.toLowerCase() && item.id !== scheme.id
                })
                if (isSchemeNameExist) {
                    this.$bkMessage({
                        message: i18n.t('方案名称已存在（不区分大小写）'),
                        theme: 'warning'
                    })
                    return
                }
                this.$validator.validateAll().then(async (result) => {
                    if (!result) return
                    try {
                        scheme.isLoading = true
                        const selectedNodes = this.selectedNodes.slice()
                        const resp = await this.updateTaskScheme({
                            isCommon: this.isCommonProcess,
                            data: JSON.stringify(selectedNodes),
                            name: scheme.name,
                            id: scheme.id
                        })
                        if (!resp.result) return
                        scheme.isEdit = false
                        scheme.isLoading = false
                        const index = this.schemeList.findIndex(item => item.id === scheme.id)
                        this.schemeList.splice(index, 1, {
                            ...scheme,
                            ...resp.data,
                            isChecked: true
                        })
                        this.$bkMessage({
                            message: i18n.t('方案修改成功'),
                            theme: 'success'
                        })
                    } catch (error) {
                        scheme.isLoading = false
                        console.warn(error)
                    }
                })
            },
            onCancelUpdateScheme (scheme) {
                Object.assign(scheme, scheme.initScheme || {})
                // 删除多余字段
                delete scheme.initScheme
                // 取消后恢复到编辑前的选中效果
                if (this.previousCheckedScheme.length) {
                    this.schemeList.forEach(item => {
                        item.isChecked = this.previousCheckedScheme.includes(item.id)
                    })
                    this.previousCheckedScheme = []
                }
                // 取消编辑后，画布按编辑前选中的方案来勾选节点
                this.$emit('setCanvasSelected', [...this.previousCheckedNode])
                this.previousCheckedNode = []
            },
            /**
             * 删除方案
             */
            onDeleteScheme (scheme) {
                if (scheme.quote_count > 0) return
                const tplAction = this.isCommonProcess ? 'common_flow_edit' : 'flow_edit'
                const hasPermission = this.checkSchemeRelativePermission([tplAction])

                if (!hasPermission) return
                const h = this.$createElement
                this.$bkInfo({
                    subHeader: h('div', { class: 'custom-header' }, [
                        h('div', {
                            class: 'custom-header-title',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('确认删除执行方案【n】?', { n: scheme.name })])
                    ]),
                    extCls: 'dialog-custom-header-title',
                    maskClose: false,
                    width: 450,
                    confirmLoading: true,
                    cancelText: this.$t('取消'),
                    confirmFn: async () => {
                        await this.onDeleteConfirm(scheme)
                    }
                })
            },
            // 确认删除
            async onDeleteConfirm (scheme) {
                try {
                    scheme.isLoading = true
                    if (scheme.isDefault) {
                        scheme.isDefault = false
                        await this.onSaveDefaultExecuteScheme()
                    }
                    await this.deleteTaskScheme({
                        isCommon: this.isCommonProcess,
                        id: scheme.id
                    })
                    const index = this.schemeList.findIndex(item => item.id === scheme.id)
                    this.schemeList.splice(index, 1)
                    this.onCheckChange(scheme)
                    this.$bkMessage({
                        message: i18n.t('方案删除成功'),
                        theme: 'success'
                    })
                } catch (error) {
                    console.warn(error)
                } finally {
                    scheme.isLoading = false
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
    .scheme-list-panel {
        position: absolute;
        top: 0;
        right: 0;
        width: 490px;
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
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 16px;
            padding: 0 22px 0 20px;
            color: #313238;
            border-bottom: 1px solid #dcdee5;
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
        .single-use-alert {
            margin: 20px 22px -5px 20px;
            .single-use {
                color: #3a84ff;
                cursor: pointer;
            }
        }
        .scheme-active-wrapper {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 20px 22px 0 20px;
            .bk-button {
                width: auto;
                margin-left: 10px;
                &:first-child {
                    width: 80px;
                    margin-left: 0;
                }
            }
        }
        .scheme-wrapper {
            border: 1px solid #dee0e6;
            margin: 15px 22px 15px 20px;
            max-height: calc(100% - 136px);
            .scheme-list {
                height: calc(100% - 41px);
                overflow: hidden;
                overflow-y: auto;
                @include scrollbar;
            }
            .scheme-title, .scheme-item {
                position: relative;
                min-height: 42px;
                display: flex;
                align-items: center;
                flex-wrap: wrap;
                font-size: 12px;
                padding: 5px 0 5px 12px;
                border-bottom: 1px solid #ebebeb;
            }
            .scheme-name {
                max-width: 310px;
                margin-left: 10px;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
                color: #313238;
            }
            .quoted-count {
                margin-left: 7px;
                color: #979ba5;
            }
            .icon-btn-wrapper {
                position: absolute;
                top: 15px;
                right: 10px;
                display: flex;
                align-items: center;
                i {
                    font-size: 16px;
                    cursor: pointer;
                    color: #979ba5;
                    font-weight: 500;
                    opacity: 0;
                    transition: opacity .5s;
                    &:not(:first-child) {
                        margin-left: 12px;
                    }
                    &:not(.common-icon-default):hover {
                        color: #3a84ff !important;
                    }
                    &.disabled {
                        color: #c4c6cc;
                        cursor: not-allowed;
                    }
                    &.is-default {
                        color: #3a84ff;
                        opacity: 1;
                    }
                    &:hover {
                        opacity: 1;
                    }
                }
                .common-icon-default {
                    font-size: 14px;
                    margin-top: 1px;
                }
            }
            .scheme-title {
                background: #fafbfd;
                border-top: none;
            }
            .scheme-item {
                &:hover {
                    background-color: #f0f1f5;
                    .icon-btn-wrapper i {
                        opacity: 1;
                    }
                }
                &.is-edited {
                    background: #eaf3ff;
                    .icon-btn-wrapper i {
                        opacity: 1;
                    }
                }
                &.is-checked {
                    background: #eaf3ff;
                }
                &:last-child {
                    border-bottom: none;
                }
            }
            .add-scheme {
                position: relative;
                padding: 4px 0 5px 12px;
                border-bottom: 1px solid #f0f1f5;
                .icon-btn-wrapper i {
                    opacity: 1;
                }
                .common-error-tip {
                    display: none;
                }
                &.is-empty {
                    border-bottom: none;
                }
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
    .scheme-nav {
        position: absolute;
        right: 0;
        top: 20px;
        display: flex;
        align-items: center;
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
            margin-right: 3px;
        }
    }
    .bk-input-inline {
        display: inline-block;
        width: 374px;
    }
    .no-data-wrapper {
        height: auto;
        padding: 22px 0 32px;
    }
</style>
