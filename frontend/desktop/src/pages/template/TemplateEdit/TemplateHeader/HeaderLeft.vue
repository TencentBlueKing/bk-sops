<template>
    <div class="header-left">
        <!--头部左侧-->
        <div class="header-left-area">
            <i class="bk-icon icon-arrows-left back-icon" @click="onBackClick"></i>
            <span class="label">{{ isViewMode ? '正式' : '草稿' }}</span>
            <a
                v-if="['view', 'edit'].includes(type)"
                data-test-id="templateDetail_header_collectBtn"
                href="javascript:void(0);"
                class="common-icon-favorite icon-favorite"
                :class="{
                    'is-active': isCollected
                }"
                @click="onCollectTemplate">
            </a>
            <span v-bk-overflow-tips class="template-name">{{ name }}</span>
            <i
                class="bk-icon icon-edit-line"
                :class="{ 'is-active': infoDialogShow }"
                data-test-id="templateDetail_header_editInfoBtn"
                @click="onOpenTplBasicDialog">
            </i>
        </div>
        <bk-dialog
            width="480"
            ext-cls="common-dialog label-dialog"
            header-position="left"
            render-directive="if"
            :mask-close="false"
            :auto-close="false"
            :title="$t('修改基本信息')"
            :loading="saveInfoLoading"
            :value="infoDialogShow"
            :cancel-text="$t('取消')"
            @confirm="editInfoConfirm"
            @cancel="infoDialogShow = false">
            <bk-form
                ref="configForm"
                class="form-area"
                form-type="vertical"
                :model="formData"
                :label-width="140"
                :rules="rules">
                <bk-form-item :property="'name'" class="template-name-input" data-test-id="tabTemplateConfig_form_name">
                    <bk-input
                        ref="nameInput"
                        v-model.trim="formData.name"
                        :placeholder="$t('请输入流程模板名称')"
                        :maxlength="stringLength.TEMPLATE_NAME_MAX_LENGTH"
                        :show-word-limit="true">
                    </bk-input>
                </bk-form-item>
                <bk-form-item v-if="!common" :label="$t('标签')" data-test-id="tabTemplateConfig_form_label">
                    <bk-select
                        :key="templateLabels.length"
                        v-model="formData.labels"
                        ext-popover-cls="label-select-popover"
                        :display-tag="true"
                        :multiple="true"
                        searchable
                        :popover-options="{
                            onHide: () => !labelDialogShow
                        }">
                        <div class="label-select-content" v-bkloading="{ isLoading: templateLabelLoading }">
                            <bk-option
                                v-for="(item, index) in templateLabels"
                                :key="index"
                                :id="item.id"
                                :name="item.name">
                                <div class="label-select-option">
                                    <span
                                        class="label-select-color"
                                        :style="{ background: item.color }">
                                    </span>
                                    <span>{{item.name}}</span>
                                    <i class="bk-option-icon bk-icon icon-check-1"></i>
                                </div>
                            </bk-option>
                        </div>
                        <div slot="extension" class="label-select-extension">
                            <div
                                class="add-label"
                                data-test-id="tabTemplateConfig_form_editLabel"
                                v-cursor="{ active: !hasPermission(['project_edit'], authActions) }"
                                @click="onEditLabel">
                                <i class="bk-icon icon-plus-circle"></i>
                                <span>{{ $t('新建标签') }}</span>
                            </div>
                            <div
                                class="label-manage"
                                data-test-id="tabTemplateConfig_form_LabelManage"
                                v-cursor="{ active: !hasPermission(['project_view'], authActions) }"
                                @click="onManageLabel">
                                <i class="common-icon-label"></i>
                                <span>{{ $t('标签管理') }}</span>
                            </div>
                            <div
                                class="refresh-label"
                                data-test-id="process_list__refreshLabel"
                                @click="$emit('updateTemplateLabelList')">
                                <i class="bk-icon icon-right-turn-line"></i>
                            </div>
                        </div>
                    </bk-select>
                </bk-form-item>
                <bk-form-item property="notifyType" :label="$t('流程描述')" data-test-id="tabTemplateConfig_form_notifyType">
                    <bk-input
                        type="textarea"
                        v-model.trim="formData.description"
                        :rows="5"
                        :placeholder="$t('请输入流程模板备注信息')"
                        :maxlength="100"
                        :show-word-limit="true">
                    </bk-input>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
        <!--新建标签dialog-->
        <bk-dialog
            width="480"
            ext-cls="common-dialog label-dialog"
            header-position="left"
            render-directive="if"
            :mask-close="false"
            :auto-close="false"
            :title="$t('新建标签')"
            :loading="labelLoading"
            :value="labelDialogShow"
            :cancel-text="$t('取消')"
            @confirm="editLabelConfirm"
            @cancel="labelDialogShow = false">
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
    </div>
</template>

<script>
    import { NAME_REG, STRING_LENGTH, LABEL_COLOR_LIST } from '@/constants/index.js'
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import permission from '@/mixins/permission.js'
    export default {
        name: 'HeaderLeft',
        mixins: [permission],
        props: {
            type: String,
            name: String,
            template_id: [String, Number],
            project_id: [String, Number],
            common: String,
            templateSaving: Boolean,
            isTemplateDataChanged: Boolean,
            tplActions: {
                type: Array,
                default () {
                    return []
                }
            },
            collectInfo: {
                type: Object,
                default: () => ({})
            }
        },
        data () {
            const { name, template_labels, description } = this.$store.state.template
            const { isCollected, collectionId } = this.collectInfo
            return {
                formData: {
                    name,
                    labels: [...template_labels],
                    description
                },
                stringLength: STRING_LENGTH,
                rules: {
                    name: [
                        {
                            required: true,
                            message: i18n.t('必填项'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH,
                            message: i18n.t('流程名称长度不能超过') + STRING_LENGTH.TEMPLATE_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        },
                        {
                            regex: NAME_REG,
                            message: i18n.t('流程名称不能包含') + '\'‘"”$&<>' + i18n.t('非法字符'),
                            trigger: 'blur'
                        }
                    ]
                },
                templateLabelLoading: false,
                templateLabels: [],
                labelDialogShow: false,
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
                                return this.templateLabels.every(label => label.name !== val)
                            },
                            message: i18n.t('标签已存在，请重新输入'),
                            trigger: 'blur'
                        }
                    ]
                },
                labelDetail: {},
                colorDropdownShow: false,
                colorList: LABEL_COLOR_LIST,
                labelLoading: false,
                saveInfoLoading: false,
                isCollected,
                collectionId,
                infoDialogShow: false
            }
        },
        computed: {
            ...mapState({
                'username': state => state.username
            }),
            ...mapState('project', {
                'authActions': state => state.authActions,
                'projectName': state => state.projectName
            }),
            isViewMode () {
                return this.type === 'view'
            }
        },
        watch: {

        },
        methods: {
            ...mapActions([
                'addToCollectList',
                'deleteCollect'
            ]),
            ...mapMutations('template/', [
                'setTplConfig'
            ]),
            ...mapActions('template/', [
                'updateTemplateData'
            ]),
            ...mapActions('project/', [
                'getProjectLabelsWithDefault',
                'createTemplateLabel'
            ]),
            // 返回按钮点击
            onBackClick () {
                if (this.isTemplateDataChanged && this.type === 'edit') {
                    this.$emit('goBackViewMode') // 编辑态下返回上一个路由时先保存再back
                } else if (window.history.length <= 1) {
                    const { name } = this.$route
                    const url = name === 'projectCommonTemplatePanel'
                        ? { name: 'processCommon', params: { project_id: this.project_id } }
                        : this.common
                            ? { name: 'commonProcessList' }
                            : { name: 'processHome', params: { project_id: this.project_id } }
                    this.$router.push(url)
                } else if (this.$parent.isRouterPush) {
                    this.$router.go(-2)
                } else {
                    this.$router.back() // 由模板页跳转进入需要保留分页参数
                }
            },
            // 编辑模板基础信息
            onOpenTplBasicDialog () {
                this.infoDialogShow = !this.infoDialogShow
                if (this.infoDialogShow) {
                    this.getTemplateLabelList()
                }
            },
            /**
             * 加载模板标签列表
             */
            async getTemplateLabelList () {
                try {
                    this.templateLabelLoading = true
                    const res = await this.getProjectLabelsWithDefault(this.project_id)
                    this.templateLabels = res.data
                } catch (e) {
                    console.log(e)
                } finally {
                    this.templateLabelLoading = false
                }
            },
            async editInfoConfirm () {
                try {
                    this.saveInfoLoading = true
                    const { name, description, labels } = this.formData
                    this.setTplConfig({
                        name,
                        description,
                        template_labels: labels
                    })
                    if (['view', 'edit'].includes(this.type)) {
                        await this.updateTemplateData({
                            common: this.common,
                            projectId: this.project_id,
                            templateId: this.template_id
                        })
                    }
                    this.infoDialogShow = false
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.saveInfoLoading = false
                }
            },
            onEditLabel () {
                if (!this.hasPermission(['project_edit'], this.authActions)) {
                    const resourceData = {
                        project: [{
                            id: this.project_id,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission(['project_edit'], this.authActions, resourceData)
                    return
                }
                this.labelDetail = { color: '#1c9574', name: '', description: '' }
                this.labelDialogShow = true
                this.colorDropdownShow = false
            },
            onManageLabel () {
                if (!this.hasPermission(['project_view'], this.authActions)) {
                    const resourceData = {
                        project: [{
                            id: this.project_id,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission(['project_view'], this.authActions, resourceData)
                    return
                }
                const { href } = this.$router.resolve({
                    name: 'projectConfig',
                    params: { id: this.project_id },
                    query: { configActive: 'label_config' }
                })
                window.open(href, '_blank')
            },
            editLabelConfirm () {
                if (this.labelLoading) {
                    return
                }
                this.labelLoading = true
                try {
                    this.$refs.labelForm.validate().then(async result => {
                        if (result) {
                            const { color, name, description } = this.labelDetail
                            const data = {
                                creator: this.username,
                                project_id: Number(this.project_id),
                                color,
                                name,
                                description
                            }
                            const resp = await this.createTemplateLabel(data)
                            if (resp.result) {
                                this.getTemplateLabelList()
                                this.labelDialogShow = false
                                this.formData.labels.push(resp.data.id)
                                this.$bkMessage({
                                    message: i18n.t('标签新建成功'),
                                    theme: 'success'
                                })
                            }
                        }
                    })
                } catch (e) {
                    console.log(e)
                } finally {
                    this.labelLoading = false
                }
            },
            // 添加/取消收藏模板
            async onCollectTemplate () {
                try {
                    if (!this.isCollected) { // add
                        const extraInfo = {
                            template_id: this.template_id,
                            name: this.name,
                            id: this.template_id
                        }
                        if (!this.common) {
                            extraInfo.project_id = this.project_id
                            extraInfo.project_name = this.projectName
                        }
                        const res = await this.addToCollectList([{
                            extra_info: extraInfo,
                            instance_id: this.template_id,
                            username: this.username,
                            category: this.common ? 'common_flow' : 'flow'
                        }])
                        if (res.data.length) {
                            this.$bkMessage({ message: i18n.t('添加收藏成功！'), theme: 'success' })
                        }
                        this.collectionId = res.data[0].id
                    } else { // cancel
                        await this.deleteCollect(this.collectionId)
                        this.$bkMessage({ message: i18n.t('取消收藏成功！'), theme: 'success' })
                        this.collectionId = ''
                    }
                    this.isCollected = !this.isCollected
                } catch (e) {
                    console.log(e)
                } finally {
                    this.collectingId = ''
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    .header-left-area {
        flex: 1;
        display: flex;
        align-items: center;
        height: 100%;
        .back-icon {
            font-size: 28px;
            color: #3a84ff;
            cursor: pointer;
        }
        .label {
            flex-shrink: 0;
            font-size: 12px;
            line-height: 20px;
            padding: 0 8px;
            margin-right: 8px;
            color: #14a568;
            background: #e4faf0;
            border: 1px solid #a5e0c6;
            border-radius: 2px;
        }
        .template-name {
            color: #63656e;
            margin-right: 9px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .icon-favorite {
            font-size: 14px;
            color: #c4c6cc;
            margin: 1px 8px 0 0;
            &.is-active {
                display: block;
                color: #ff9c01;
            }
        }
        .icon-edit-line {
            width: 24px;
            height: 24px;
            display: none;
            text-align: center;
            line-height: 24px;
            font-size: 16px;
            color: #979ba5;
            background: #f0f1f5;
            border-radius: 2px;
            cursor: pointer;
            &.is-active,
            &:hover {
                display: inline-block;
                color: #3a84ff;
                background: #e1ecff;
            }
        }
    }
    .form-area {
        margin: -2px 24px 24px;
        padding: 0;
    }
</style>
