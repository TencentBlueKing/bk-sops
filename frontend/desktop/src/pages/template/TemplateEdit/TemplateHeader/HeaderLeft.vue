<template>
    <div class="header-left">
        <!--头部左侧-->
        <div class="header-left-area">
            <i class="bk-icon icon-arrows-left back-icon" @click="onBackClick"></i>
            <span class="label">{{ type === 'view' ? '正式' : '草稿' }}</span>
            <span v-bk-overflow-tips class="template-name">{{ name }}</span>
            <i class="common-icon-tooltips" v-bk-tooltips="tplBasicInfoTipsConfig"></i>
            <span v-if="!isViewMode" class="bk-icon icon-edit2" @click="onOpenTplBasicDialog"></span>
        </div>
        <!--模板基础信息tips-->
        <div class="tpl-basic-info" id="tplBasicInfoHtml">
            <p class="tag-label">{{ '标签' }}</p>
            <ul class="tag-list">
                <template v-if="labelTagList && labelTagList.length">
                    <div
                        v-for="tag in labelTagList"
                        :key="tag.id"
                        class="tag-item"
                        :style="{ background: tag.color, color: darkColorList.includes(tag.color) ? '#fff' : '#262e4f' }">
                        {{ tag.name }}
                    </div>
                </template>
                <span v-else>{{ '--' }}</span>
            </ul>
            <p class="desc-label mt10">{{ '描述' }}</p>
            <div class="desc">{{ formData.description || '--' }}</div>
        </div>
        <!--模板基础信息编辑-->
        <bk-dialog
            v-model="tplBasicDialogShow"
            theme="primary"
            render-directive="if"
            :mask-close="false"
            :width="480"
            ext-cls="tpl-basic-dialog"
            header-position="left"
            :title="$t('修改基本信息')">
            <bk-form
                ref="configForm"
                class="form-area"
                :model="formData"
                :label-width="140"
                :rules="rules">
                <bk-form-item :property="'name'" :label="$t('流程名称')" :required="true" data-test-id="tabTemplateConfig_form_name">
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
                        :value="formData.labels"
                        ext-popover-cls="label-select-popover"
                        :display-tag="true"
                        :multiple="true"
                        searchable>
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
                        <!-- <div slot="extension" class="label-select-extension">
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
                        </div> -->
                    </bk-select>
                </bk-form-item>
                <bk-form-item property="notifyType" :label="$t('流程描述')" data-test-id="tabTemplateConfig_form_notifyType">
                    <bk-input
                        type="textarea"
                        v-model.trim="formData.description"
                        :rows="5"
                        :placeholder="$t('请输入流程模板备注信息')">
                    </bk-input>
                </bk-form-item>
            </bk-form>
        </bk-dialog>
    </div>
</template>

<script>
    import { NAME_REG, STRING_LENGTH, DARK_COLOR_LIST } from '@/constants/index.js'
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'
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
            }
        },
        data () {
            const { name, template_labels, description } = this.$store.state.template
            return {
                tplBasicInfoTipsConfig: {
                    allowHtml: true,
                    theme: 'light',
                    offset: '-22, 0',
                    extCls: 'info-label-tips',
                    content: '#tplBasicInfoHtml',
                    placement: 'bottom-start'
                },
                
                tplBasicDialogShow: false,
                formData: {
                    name,
                    labels: template_labels,
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
                darkColorList: DARK_COLOR_LIST
            }
        },
        computed: {
            ...mapState('project', {
                'authActions': state => state.authActions
            }),
            isViewMode () {
                return this.type === 'view'
            },
            labelTagList () {
                const { labels = [] } = this.formData
                if (labels.length) {
                    return this.templateLabels.reduce((acc, cur) => {
                        if (labels.includes(cur.id)) {
                            acc.push({ id: cur.id, name: cur.name, color: cur.color })
                        }
                        return acc
                    }, [])
                }
                return []
            }
        },
        mounted () {
            this.getTemplateLabelList()
        },
        methods: {
            ...mapActions('project/', [
                'getProjectLabelsWithDefault'
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
                this.tplBasicDialogShow = true
                this.getTemplateLabelList()
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
        .common-icon-tooltips {
            color: #979ba5;
            margin-top: 2px;
        }
        .icon-edit2 {
            font-size: 28px;
            color: #979ba5;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
        }
    }
</style>
<style lang="scss">
    .tpl-basic-info {
        min-width: 160px;
        font-size: 12px;
        margin: -2px 15px 10px 2px;
        .tag-label,
        .desc-label {
            color: #979ba5;
            letter-spacing: 0;
            line-height: 26px;
            margin-bottom: 2px;
        }
        .tag-list {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            .tag-item {
                line-height: 22px;
                padding: 1px 8px;
                margin: 0 8px 8px 0;
                color: #63656e;
                background: #f0f1f5;
                border-radius: 2px;
            }
        }
        .desc {
            color: #313238;
            line-height: 22px;
        }
    }
    .tpl-basic-dialog {
        .bk-dialog-header {
            padding-bottom: 0;
        }
        .bk-dialog-body {
            padding-top: 0;
        }
        .bk-form-item {
            margin-top: 24px;
            .bk-label {
                float: inherit;
                text-align: left;
            }
            .bk-form-content {
                float: inherit;
                margin-left: 0 !important;
            }
        }
    }
</style>
