<template>
    <bk-sideslider
        :is-show="isShow"
        :width="960"
        ext-cls="template-shared-slider"
        :transfer="true"
        :quick-close="true"
        :before-close="onClose">
        <template slot="header">
            <p class="header-title">{{ $t('共享到SRE商店') }}</p>
            <div class="help-doc" @click="jumpHelpDoc">
                <i class="common-icon-help"></i>
                <span>{{ $t('帮助文档') }}</span>
            </div>
        </template>
        <template slot="content">
            <bk-alert type="warning">
                <i18n slot="title" tag="div" path="templateSharedTips">
                    <span class="sre-store-link" @click="jumpSreStore">
                        {{ $t('SRE商店') }}
                        <span class="common-icon-jump-link"></span>
                    </span>
                </i18n>
            </bk-alert>
            <bk-form form-type="vertical" :model="formData" ref="formRef" class="mt5">
                <bk-form-item :label="$t('共享类型')" :required="true">
                    <div class="bk-button-group">
                        <bk-button
                            :class="{ 'is-selected': formData.type === 'create' }"
                            @click="toggleSharedType('create')">
                            {{ $t('新建') }}
                        </bk-button>
                        <bk-button
                            :class="{ 'is-selected': formData.type === 'update' }"
                            @click="toggleSharedType('update')">
                            {{ $t('更新') }}
                        </bk-button>
                    </div>
                </bk-form-item>
                <bk-form-item :label="$t('场景名称')" property="name" :required="true" :rules="rules.name">
                    <bk-input
                        v-if="formData.type === 'create'"
                        :placeholder="$t('请输入场景名称')"
                        minlength="2"
                        maxlength="50"
                        show-word-limit
                        v-model="formData.name"
                        @focus="repeatSceneInfo = {}">
                    </bk-input>
                    <bk-select
                        v-else
                        v-model="formData.id"
                        :placeholder="$t('请选择场景名称')"
                        :loading="recordLoading"
                        searchable
                        @selected="onSceneNameSelect">
                        <bk-option v-for="option in recordList"
                            :key="option.id"
                            :id="option.id"
                            :name="option.name">
                        </bk-option>
                    </bk-select>
                    <p v-if="repeatSceneInfo.url" class="scene-repeat-tips">
                        <span>{{ $t('场景名称重复：') }}</span>
                        <a target="_blank" :href="repeatSceneInfo.url">
                            {{ repeatSceneInfo.scene_name }}
                            <i class="common-icon-jump-link"></i>
                        </a>
                    </p>
                </bk-form-item>
                <bk-form-item :label="$t('场景分类')" property="category" :required="true" :rules="rules.required">
                    <bk-select
                        :disabled="formData.type === 'update'"
                        v-model="formData.category"
                        :loading="marketLoading"
                        :show-empty="!categoryList.length">
                        <div
                            slot="trigger"
                            class="bk-select-name category-select"
                            :data-placeholder="categorySelectPath ? '' : $t('请选择场景分类')">
                            {{ categorySelectPath }}
                            <i class="bk-select-angle bk-icon icon-angle-down"></i>
                        </div>
                        <bk-big-tree
                            ref="categoryTree"
                            :data="categoryList"
                            :selectable="true"
                            :show-link-line="false"
                            :show-icon="false"
                            :options="{
                                idKey: 'code_path'
                            }"
                            :before-select="(node) => !node.children.length"
                            @select-change="onCategorySelect">
                        </bk-big-tree>
                    </bk-select>
                </bk-form-item>
                <bk-form-item :label="$t('标签')" :desc="$t('场景使用者通过标签可以快速找到同一类场景')">
                    <SharedTagSelect
                        v-model="formData.labels"
                        :loading="marketLoading"
                        :tag-list.sync="tagList">
                    </SharedTagSelect>
                </bk-form-item>
                <bk-form-item
                    :label="$t('风险级别')"
                    property="risk_level"
                    :required="true"
                    :rules="rules.required"
                    :desc="$t('申明该场景的运维操作风险级别，以便场景使用者决策场景的使用方式')">
                    <bk-radio-group v-model="formData.risk_level">
                        <bk-radio
                            v-for="item in riskLevelList"
                            :key="item.risk_level"
                            :value="item.risk_level">
                            {{ item.risk_name }}
                        </bk-radio>
                    </bk-radio-group>
                </bk-form-item>
                <bk-form-item :label="$t('使用说明')">
                    <MarkdownEditor v-model="formData.usage_content.content"></MarkdownEditor>
                </bk-form-item>
            </bk-form>
        </template>
        <template slot="footer">
            <bk-button theme="primary" :loading="saveLoading" @click="onSave">{{ $t('确定') }}</bk-button>
            <bk-button :disabled="saveLoading" @click="onClose">{{ $t('取消') }}</bk-button>
        </template>
    </bk-sideslider>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import tools from '@/utils/tools.js'
    import { mapActions, mapState } from 'vuex'
    import SharedTagSelect from './SharedTagSelect.vue'
    import MarkdownEditor from './markdownEditor/editor.vue'
    export default {
        components: {
            SharedTagSelect,
            MarkdownEditor
        },
        props: {
            isShow: {
                type: Boolean,
                default: false
            },
            selected: {
                type: Array,
                default: () => ([])
            },
            project_id: [String, Number]
        },
        data () {
            const defaultEditorContent = [
                '## 1. 背景',
                '*为什么要开发这个场景*',
                '## 2. 适用场景',
                '*这个场景解决什么问题*',
                '## 3.使用流程',
                '### 3.1 前置条件',
                '*如有*',
                '### 3.2 xxx',
                '## 4. FAQ'
            ]
            const formData = {
                id: undefined,
                type: 'create',
                name: '',
                category: '',
                labels: [],
                risk_level: '',
                usage_content: { content: defaultEditorContent.join('\n\n') }
            }
            return {
                formData: tools.deepClone(formData),
                defaultFormData: tools.deepClone(formData),
                rules: {
                    name: [{
                        required: true,
                        message: i18n.t('必填项'),
                        trigger: 'blur'
                    }, {
                        min: 3,
                        message: i18n.t('场景名称长度最小3个字符'),
                        trigger: 'blur'
                    }],
                    required: [{
                        required: true,
                        message: i18n.t('必填项'),
                        trigger: 'blur'
                    }]
                },
                recordLoading: false,
                recordList: [],
                marketLoading: false,
                categoryList: [],
                tagList: [],
                riskLevelList: [],
                saveLoading: false,
                repeatSceneInfo: {}
            }
        },
        computed: {
            ...mapState({
                'infoBasicConfig': state => state.infoBasicConfig,
                'username': state => state.username
            }),
            categorySelectPath () {
                return this.findPathByCodePath(this.categoryList, this.formData.category)
            }
        },
        watch: {
            isShow (val) {
                if (val) {
                    this.getMarketConfig()
                } else {
                    this.formData = tools.deepClone(this.defaultFormData)
                }
            }
        },
        methods: {
            ...mapActions('templateMarket/', [
                'loadMarkedServiceCategory',
                'loadMarkedSceneLabel',
                'loadMarkedRiskLevel',
                'sharedTemplateRecord',
                'loadSharedTemplateRecord'
            ]),
            async getMarketConfig () {
                try {
                    this.marketLoading = true
                    const [resp1, resp2, resp3] = await Promise.all([
                        this.loadMarkedServiceCategory(),
                        this.loadMarkedSceneLabel(),
                        this.loadMarkedRiskLevel()
                    ])
                    this.categoryList = resp1.data
                    this.tagList = resp2.data
                    this.riskLevelList = resp3.data
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.marketLoading = false
                }
            },
            jumpHelpDoc () {
                window.open(window.TEMPLATE_MARKET_DOC_URL, '_target')
            },
            jumpSreStore () {
                window.open(window.TEMPLATE_MARKET_HOST, '_target')
            },
            toggleSharedType (type) {
                const resetFormData = () => {
                    this.formData = {
                        ...tools.deepClone(this.defaultFormData),
                        type
                    }
                    this.$refs.formRef.clearError()
                }
                const refreshData = () => {
                    resetFormData()
                    this.getSharedRecordList()
                }

                if (type !== 'update') {
                    refreshData()
                    return
                }

                const isDataModified = !tools.isDataEqual(this.formData, this.defaultFormData)
                if (!isDataModified) {
                    refreshData()
                    return
                }

                this.$bkInfo({
                    type: 'warning',
                    title: i18n.t('将清空输入信息'),
                    confirmFn: refreshData
                })
            },
            async getSharedRecordList () {
                try {
                    this.recordLoading = true
                    const resp = await this.loadSharedTemplateRecord()
                    this.recordList = resp.data
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.recordLoading = false
                }
            },
            onSceneNameSelect (val) {
                const selectInfo = this.recordList.find(item => item.id === val) || {}
                const { risk_level: riskLevel, usage_content: content } = selectInfo
                Object.assign(this.formData, selectInfo, {
                    risk_level: String(riskLevel),
                    usage_content: { content }
                })
            },
            onCategorySelect (node) {
                this.formData.category = node.id
            },
            findPathByCodePath (categoryList, targetCodePath) {
                const traverse = (node, path) => {
                    const currentPath = [...path, node.name]
                    if (node.code_path === targetCodePath) {
                        return currentPath
                    }

                    for (const child of node.children || []) {
                        const result = traverse(child, currentPath)
                        if (result) {
                            return result
                        }
                    }

                    return null
                }

                for (const rootNode of categoryList) {
                    const result = traverse(rootNode, [])
                    if (result) {
                        return result.join('/')
                    }
                }

                return null
            },
            onSave () {
                this.$refs.formRef.validate().then(async result => {
                    try {
                        if (!result) return
                        this.saveLoading = true
                        const params = {
                            ...this.formData,
                            project_code: this.project_id,
                            creator: this.username
                        }

                        const selectedTplIds = this.selected.map(item => item.id)
                        // 更新
                        if (params.id) {
                            const existTplIds = params.templates.map(item => item.id)
                            selectedTplIds.push(...existTplIds)
                        }
                        params.templates = [...new Set(selectedTplIds)]

                        const resp = await this.sharedTemplateRecord(params)
                        this.repeatSceneInfo = {
                            ...resp.data,
                            result: resp.result
                        }
                        if (!resp.result) return

                        this.showSuccessMessage()
                        this.$emit('close')
                    } catch (error) {
                        console.warn(error)
                    } finally {
                        this.saveLoading = false
                    }
                })
            },
            showSuccessMessage () {
                const h = this.$createElement
                const messageContent = h('i18n', {
                    attrs: {
                        path: 'templateSharedSuccessTips',
                        tag: 'div'
                    },
                    on: {
                        click: () => {
                            window.open(this.repeatSceneInfo.scene_url, '_target')
                        }
                    }
                }, [
                    h('span', {
                        style: {
                            cursor: 'pointer',
                            color: '#3a84ff'
                        }
                    }, [
                        i18n.t('SRE商店'),
                        h('span', {
                            class: 'common-icon-jump-link'
                        })
                    ])
                ])

                this.$bkMessage({
                    message: messageContent,
                    theme: 'success'
                })
            },
            onClose () {
                const isDataEqual = tools.isDataEqual(this.formData, this.defaultFormData)
                if (!isDataEqual) {
                    this.$bkInfo({
                        ...this.infoBasicConfig,
                        confirmFn: () => {
                            this.$emit('close')
                        }
                    })
                } else {
                    this.$emit('close')
                }
            }
        }
    }
</script>
<style lang="scss">
    .template-shared-slider {
        .bk-sideslider-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 26px 0 16px !important;
            border-bottom: 1px solid #dcdee5;
            .help-doc {
                font-size: 14px;
                color: #979BA5;
                cursor: pointer;
                &:hover {
                    color: #3a84ff;
                }
            }
        }
        .bk-sideslider-content {
            height: calc(100vh - 114px);
            padding: 12px 35px;
            .sre-store-link {
                color: #3a84ff;
                cursor: pointer;
                .common-icon-jump-link {
                    font-size: 14px;
                }
            }
            .bk-button-group {
                button {
                    width: 216px;
                }
            }
            .bk-form-radio {
                margin-right: 24px;
            }
            .shared-illustrate-input {
                min-height: 376px;
                border-color: #dcdee5;
                .v-note-op {
                    border-color: #dcdee5;
                }
            }
            .scene-repeat-tips {
                display: flex;
                align-items: center;
                line-height: 16px;
                margin-top: 3px;
                font-size: 12px;
                span {
                    color: #ff5656;
                }
                a {
                    color: #3a84ff;
                    .common-icon-jump-link {
                        font-size: 14px;
                    }
                }
            }
            .category-select::before {
                position: absolute;
                content: attr(data-placeholder);
                color: #c4c6cc;
            }
        }
        .bk-sideslider-footer {
            padding-left: 24px;
            box-shadow: 0 -1px 0 0 #dcdee5;
            button {
                width: 88px;
                margin-right: 8px;
            }
        }
    }
</style>
