<template>
    <div class="edit-task-scheme" v-if="isSchemeShow">
        <div class="scheme-nav" @click="toggleSchemePanel">
            <i class="bk-icon icon-angle-left"></i>
            {{ $t('执行方案') }}
        </div>
        <div class="scheme-list-panel" v-if="showPanel">
            <div class="scheme-sideslider-header">
                <p v-if="isDefaultSchemeIng" class="default-scheme-title">
                    <span class="back-area" @click="goBackExecuteScheme">
                        <i class="bk-icon icon-arrows-left-line"></i>
                        {{$t('执行方案')}}
                    </span>
                    <span class="interval-symbol">></span>
                    <span>{{$t('设置默认方案')}}</span>
                </p>
                <template v-else>
                    <p>{{$t('执行方案')}}</p>
                    <i class="bk-icon icon-close-line" @click="toggleSchemePanel"></i>
                </template>
            </div>
            <p v-if="isDefaultSchemeIng" class="default-scheme-tip">
                {{$t('流程直接新建任务执行时，默认执行当前方案的组合。')}}
            </p>
            <div class="scheme-active-wrapper" v-else>
                <div>
                    <bk-button data-test-id="templateEdit_form_addScheme" icon="plus-line" @click="onCreateScheme">{{ $t('新增') }}</bk-button>
                    <bk-button data-test-id="templateEdit_form_importTemporaryPlan" @click="onImportTemporaryPlan">{{ $t('导入临时方案') }}</bk-button>
                    <bk-button data-test-id="templateEdit_form_setDeafultScheme" @click="onSetDefaultPlan">{{ $t('设置默认方案') }}</bk-button>
                </div>
                <bk-button
                    data-test-id="templateEdit_form_previewNode"
                    @click="onChangePreviewNode">
                    {{ isPreview ? $t('关闭预览') : $t('节点预览')}}
                </bk-button>
            </div>
            <section
                data-test-id="templateEdit_form_schemeList"
                :class="['scheme-wrapper', { 'is-default-scheme': isDefaultSchemeIng }]"
                v-bkloading="{ isLoading: isSchemeLoading }">
                <p :class="['scheme-title', { 'data-empty': !schemeList.length && !nameEditing }]">
                    <bk-checkbox
                        :value="isAllChecked"
                        :indeterminate="indeterminate"
                        v-bk-tooltips="{ content: $t('请先保存方案再执行其他操作'), boundary: 'window', disabled: !nameEditing }"
                        :disabled="!schemeList.length || nameEditing"
                        @change="onAllCheckChange">
                    </bk-checkbox>
                    <span class="scheme-name">{{ $t('方案名称') }}</span>
                </p>
                <ul class="scheme-list" v-if="schemeList.length || nameEditing">
                    <!-- 创建方案 -->
                    <li class="add-scheme" :class="{ 'vee-errors': veeErrors.has('schemeName'), 'is-mepty': !schemeList.length }" v-if="nameEditing">
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
                        <p class="common-error-tip error-msg">{{ veeErrors.first('schemeName') }}</p>
                    </li>
                    <!-- 方案展示列表 -->
                    <li
                        v-for="item in schemeList"
                        :class="['scheme-item', { 'is-checked': isDefaultSchemeIng ? item.isDefault : Boolean(planDataObj[item.uuid]) }]"
                        :key="item.uuid">
                        <bk-checkbox
                            :value="isDefaultSchemeIng ? item.isDefault : Boolean(planDataObj[item.uuid])"
                            :disabled="nameEditing"
                            v-bk-tooltips="{ content: $t('请先保存方案再执行其他操作'), boundary: 'window', disabled: !nameEditing }"
                            @change="onCheckChange($event, item)">
                        </bk-checkbox>
                        <span class="scheme-name" :title="item.name">{{item.name}}</span>
                        <span v-if="item.isDefault" class="default-label">{{$t('默认')}}</span>
                        <span v-if="item.quote_count > 0" class="quoted-count">{{ $tc('被个子流程引用', item.quote_count, { n: item.quote_count }) }}</span>
                        <p class="icon-btn-wrapper" v-if="!isDefaultSchemeIng">
                            <i
                                v-bk-tooltips="{ content: $t('编辑'), boundary: 'window' }"
                                class="bk-icon icon-edit-line"
                                @click="onEditSelectScheme(item)">
                            </i>
                            <i
                                v-bk-tooltips="{ content: $t('删除'), boundary: 'window' }"
                                :class="['bk-icon icon-delete', { disabled: item.quote_count > 0 }]"
                                @click="onDeleteScheme(item)">
                            </i>
                        </p>
                    </li>
                </ul>
                <!-- 无数据提示 -->
                <NoData v-else></NoData>
            </section>
            <section class="scheme-footer">
                <bk-button
                    data-test-id="templateEdit_form_saveScheme"
                    theme="primary"
                    :loading="executeSchemeSaving || isSaveDefaultLoading"
                    @click="onSaveExecuteSchemeClick">
                    {{ $t('保存') }}
                </bk-button>
                <bk-button
                    data-test-id="templateEdit_form_returnBtn"
                    @click="toggleSchemePanel">
                    {{ $t('返回') }}
                </bk-button>
            </section>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { uuid } from '@/utils/uuid.js'
    import tools from '@/utils/tools.js'
    import { mapState, mapActions } from 'vuex'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import permission from '@/mixins/permission.js'
    import bus from '@/utils/bus.js'
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
            planDataObj: {
                type: Object,
                default: () => {}
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
                schemeName: '',
                schemeNameRule: {
                    required: true,
                    max: STRING_LENGTH.SCHEME_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                isSchemeLoading: true,
                isDefaultSchemeIng: false,
                isSaveDefaultLoading: false,
                schemeList: [],
                initSchemeIdList: [],
                initDefaultIdList: [],
                isUpdate: false,
                defaultSchemeId: null,
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
            },
            schemeInfo (val) {
                if (!this.schemeList.length) return
                const scheme = this.schemeList.find(item => item.uuid === val.uuid)
                scheme.data = JSON.stringify(val.data)
            },
            isDefaultSchemeIng (val) {
                this.$emit('setDefaultSelected', val)
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
                'saveDefaultScheme',
                'updateDefaultScheme',
                'deleteDefaultScheme'
            ]),
            // 选择方案并进行切换更新选择的节点
            onCheckChange (e, scheme) {
                // 提示用户先保存创建方案再进行其他操作
                if (this.setRemindUserMsg()) return
                if (this.isDefaultSchemeIng) {
                    scheme.isDefault = e
                }
                this.$emit('selectScheme', scheme, e)
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
                    const defaultObj = {}
                    this.initSchemeIdList = []
                    this.schemeList.forEach(scheme => {
                        this.$set(scheme, 'isDefault', false)
                        this.$set(scheme, 'uuid', scheme.id)
                        if (this.initDefaultIdList.includes(scheme.uuid)) {
                            scheme.isDefault = true
                            defaultObj[scheme.uuid] = JSON.parse(scheme.data)
                        }
                        this.initSchemeIdList.push(scheme.uuid)
                    })
                    this.$emit('updateTaskSchemeList', this.schemeList)
                    this.$emit('setDefaultScheme', defaultObj)
                    this.$emit('setDefaultSelected', this.isDefaultSchemeIng)
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
                        this.initDefaultIdList = schemeIds
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
             * 返回执行方案
             */
            goBackExecuteScheme () {
                const isEqual = this.judgeDataEqual()
                if (isEqual) {
                    this.isDefaultSchemeIng = false
                } else {
                    this.$emit('setTaskSchemeDialog')
                }
            },
            judgeDataEqual () {
                const selectedIdList = this.schemeList.reduce((acc, cur) => {
                    if (cur.isDefault) {
                        acc.push(cur.uuid)
                    }
                    return acc
                }, [])
                return tools.isDataEqual(this.initDefaultIdList, selectedIdList)
            },
            /**
             * 重置默认执行方案
             */
            resetDefaultScheme () {
                this.schemeList.forEach(scheme => {
                    const isTrue = this.initDefaultIdList.includes(scheme.uuid)
                    if (scheme.isDefault && !isTrue) {
                        this.onCheckChange(false, scheme)
                        scheme.isDefault = isTrue
                    }
                })
                this.isDefaultSchemeIng = false
            },
            /**
             * 任务方案面板是否显示
             */
            toggleSchemePanel () {
                if (this.isDefaultSchemeIng) {
                    this.goBackExecuteScheme()
                } else {
                    this.showPanel = !this.showPanel
                }
            },
            /**
             * 导入临时方案
            */
            onImportTemporaryPlan () {
                // 提示用户先保存创建方案再进行其他操作
                if (this.setRemindUserMsg()) return
                this.$emit('onImportTemporaryPlan')
            },
            /**
             * 设置默认方案
            */
            async onSetDefaultPlan () {
                // 提示用户先保存创建方案再进行其他操作
                if (this.setRemindUserMsg()) return
                try {
                    const schemeIdList = this.schemeList.map(scheme => scheme.uuid)
                    const isEqual = tools.isDataEqual(this.initSchemeIdList, schemeIdList)
                    if (!isEqual) {
                        this.isSchemeLoading = true
                        await this.$emit('onSaveExecuteSchemeClick', true)
                    }
                    this.isDefaultSchemeIng = true
                    this.initDefaultIdList = Object.keys(this.defaultPlanDataObj).map(item => Number(item))
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isSchemeLoading = false
                }
            },
            /**
             * 保存/更新默认方案
            */
            async onSaveDefaultExecuteScheme () {
                try {
                    const ids = Object.keys(this.defaultPlanDataObj).map(item => Number(item))
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
                this.schemeName = ''
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
                const isSchemeNameExist = this.schemeList.some(item => item.name === this.schemeName)
                if (isSchemeNameExist) {
                    this.$bkMessage({
                        message: i18n.t('方案名称已存在'),
                        theme: 'warning'
                    })
                    return
                }
                this.$validator.validateAll().then(async (result) => {
                    if (!result) {
                        this.schemeName = ''
                        return
                    }
                    this.schemeName = this.schemeName.trim()
                    const selectedNodes = this.selectedNodes.slice()
                    this.schemeList.unshift({
                        data: JSON.stringify(selectedNodes),
                        name: this.schemeName,
                        uuid: uuid()
                    })
                    this.$bkMessage({
                        message: i18n.t('新增方案成功'),
                        theme: 'success'
                    })
                    this.$emit('updateTaskSchemeList', this.schemeList, true)
                    this.schemeName = ''
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
                if (this.setRemindUserMsg() || scheme.quote_count > 0) return
                const tplAction = this.isCommonProcess ? 'common_flow_edit' : 'flow_edit'
                const hasPermission = this.checkSchemeRelativePermission([tplAction])

                if (!hasPermission) return
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
            async onSaveExecuteSchemeClick () {
                try {
                    if (this.isDefaultSchemeIng) {
                        const isEqual = this.judgeDataEqual()
                        if (!isEqual) {
                            this.isSaveDefaultLoading = true
                            await this.onSaveDefaultExecuteScheme()
                        }
                        this.isDefaultSchemeIng = false
                    } else {
                        this.$emit('onSaveExecuteSchemeClick')
                    }
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isSaveDefaultLoading = false
                }
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
        padding-bottom: 56px;
        .scheme-sideslider-header {
            height: 54px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 16px;
            color: #313238;
            border-bottom: 1px solid #dcdee5;
            .back-area {
                cursor: pointer;
                color: #3a84ff;
                .icon-arrows-left-line {
                    font-weight: 700;
                    margin-right: 9px;
                }
                .interval-symbol {
                    margin: 0 3px;
                }
            }
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
        .default-scheme-tip {
            margin-top: 20px;
            font-size: 12px;
            color: #63656e;
            line-height: 20px;
        }
        .scheme-active-wrapper {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 20px;
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
            margin: 15px 0;
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
                max-width: 310px;
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
                opacity: 0;
                transition: opacity .5s;
                .bk-icon {
                    font-size: 16px;
                    cursor: pointer;
                    color: #979ba5;
                    margin-left: 12px;
                    font-weight: 500;
                    &:not(.disabled):hover {
                        color: #3a84ff !important;
                    }
                    &.disabled {
                        color: #c4c6cc;
                        cursor: not-allowed;
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
                padding: 4px 0 5px 12px;
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
        .is-default-scheme {
            margin-top: 8px;
            .scheme-list {
                height: 100%;
            }
            .scheme-title {
                display: none;
            }
        }
    }
    .scheme-nav {
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
