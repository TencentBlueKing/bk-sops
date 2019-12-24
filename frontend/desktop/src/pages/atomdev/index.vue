/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="atomdev-page">
        <div class="page-header">
            <page-title :title="i18n.title"></page-title>
            <div class="operate-area">
                <bk-button theme="primary" :disabled="!!atomStringError" @click="onDownloadClick">{{ i18n.download }}</bk-button>
                <bk-button theme="default" :disabled="!!atomStringError" @click="onOpenPreviewMode">{{ i18n.preview }}</bk-button>
                <bk-button theme="default" :disabled="isPreviewMode" @click="showUploadDialog = true">{{ i18n.import }}</bk-button>
            </div>
        </div>
        <div class="atom-edit-wrapper">
            <div class="tag-panel-col">
                <tag-panel :tags="tags" :disabled="isPreviewMode"></tag-panel>
            </div>
            <div class="form-panel-col">
                <template v-if="!atomStringError">
                    <form-panel
                        v-if="!hideFormPanel && !isPreviewMode"
                        :forms="forms"
                        @updateForm="updateForm"
                        @editForm="editForm"
                        @formSorted="formSorted">
                    </form-panel>
                </template>
                <div v-else class="error-message">{{ atomStringError }}</div>
            </div>
            <div class="config-panel-col">
                <config-panel
                    ref="configPanel"
                    :atom-config-str="atomConfigStr"
                    :api-code-str="apiCodeStr"
                    :atom-name="atomName"
                    :preview-mode="isPreviewMode"
                    @onNameChange="atomName = $event"
                    @atomEditError="atomEditError"
                    @atomConfigUpdate="atomConfigUpdate"
                    @apiCodeUpdate="apiCodeUpdate">
                </config-panel>
            </div>
        </div>
        <bk-sideslider
            :is-show="showAtomSetting"
            :quick-close="true"
            :width="600"
            :title="i18n.formSetting"
            :before-close="closeSettingPanel">
            <atom-setting
                slot="content"
                ref="atomSetting"
                v-if="showAtomSetting"
                :editing-form="editingForm"
                :atom-forms="atomForms">
            </atom-setting>
            <div slot="footer" class="slider-footer">
                <bk-button theme="primary" @click="onSaveAtomSetting">{{ i18n.confirm }}</bk-button>
                <bk-button theme="default" @click="closeSettingPanel">{{ i18n.cancel }}</bk-button>
            </div>
        </bk-sideslider>
        <bk-dialog
            v-model="showUploadDialog"
            :width="400"
            :mask-close="false"
            :title="i18n.importTitle"
            :loading="fileUploading">
            <div class="import-wrapper">
                <upload-read-file class="import-code" @uploaded="handleFormFile($event, 'formCode')">
                    <bk-button class="primary">{{ i18n.formCode }}</bk-button>
                </upload-read-file>
                <upload-read-file class="import-code" @uploaded="handleFormFile($event, 'apiCode')">
                    <bk-button class="primary">{{ i18n.apiCode }}</bk-button>
                </upload-read-file>
            </div>
        </bk-dialog>
        <bk-dialog
            v-model="previewDialogShow"
            :fullscreen="true"
            :title="i18n.preview"
            header-position="left"
            :close-icon="false">
            <div v-if="isPreviewMode" class="preview-panel">
                <render-form
                    class="render-form"
                    :scheme="atomConfig"
                    :form-option="renderFormOption"
                    v-model="renderFormData">
                </render-form>
            </div>
            <template v-slot:footer>
                <bk-button theme="default" @click="onPreviewClose">{{ i18n.close }}</bk-button>
            </template>
        </bk-dialog>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import JSZip from 'jszip'
    import { saveAs } from 'file-saver'
    import PageTitle from './PageTitle.vue'
    import TagPanel from './TagPanel.vue'
    import FormPanel from './formPanel/FormPanel.vue'
    import ConfigPanel from './configPanel/ConfigPanel.vue'
    import AtomSetting from './atomSetting/AtomSetting.vue'
    import UploadReadFile from './UploadReadFile.vue'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import importTag from './importTag.js'
    import tools from '@/utils/tools.js'
    import { COMMON_ATTRS } from '@/components/common/RenderForm/formMixins.js'
    import serializeObj from '@/utils/serializeObj.js'
    const { components: TAGS, attrs: ATTRS } = importTag()

    // 用户可配置的公共属性
    const commonEditableAttrs = {}
    Object.keys(COMMON_ATTRS).reduce((acc, cur) => {
        if (['name', 'hookable', 'validation', 'default', 'hidden'].includes(cur)) {
            commonEditableAttrs[cur] = COMMON_ATTRS[cur]
        }
        return commonEditableAttrs
    }, commonEditableAttrs)

    export default {
        name: 'AtomDev',
        components: {
            PageTitle,
            TagPanel,
            FormPanel,
            AtomSetting,
            UploadReadFile,
            ConfigPanel,
            RenderForm
        },
        data () {
            const tags = this.getTagConfigMap(TAGS)
            return {
                tags,
                forms: [],
                atomName: '',
                atomConfig: [],
                atomConfigStr: '',
                atomStringError: '',
                apiCodeStr: '',
                editingForm: {},
                isPreviewMode: false,
                showAtomSetting: false,
                hideFormPanel: false,
                showUploadDialog: false,
                previewDialogShow: false,
                fileUploading: false,
                renderFormOption: {
                    showGroup: false,
                    showHook: true,
                    showLabel: true,
                    showVarList: false
                },
                renderFormData: {},
                i18n: {
                    title: gettext('插件开发'),
                    formSetting: gettext('插件配置'),
                    preview: gettext('预览'),
                    download: gettext('下载'),
                    import: gettext('导入'),
                    importTitle: gettext('导入文件'),
                    formCode: gettext('前端代码'),
                    apiCode: gettext('后台代码'),
                    close: gettext('关闭'),
                    confirm: gettext('确认'),
                    cancel: gettext('取消')
                }
            }
        },
        computed: {
            atomForms () {
                return this.forms.map(item => {
                    return {
                        tagCode: item.config.tag_code,
                        name: item.config.attrs.name.value
                    }
                })
            }
        },
        watch: {
            forms (val) {
                this.transAtomConfig(val)
                this.atomConfigStr = serializeObj(this.atomConfig)
            }
        },
        methods: {
            getTagConfigMap (tags) {
                const tagConfigMap = {}
                Object.keys(tags).forEach(tag => {
                    const tagAttrs = { ...commonEditableAttrs, ...ATTRS[tag] }
                    const type = tag.slice(3).replace(/[A-Z]/g, match => {
                        return `_${match.toLowerCase()}`
                    }).slice(1)
                    const attrs = {} // 对应标准插件配置项中的 attrs 属性
                    Object.keys(tagAttrs).reduce((acc, cur) => {
                        const item = tools.deepClone(tagAttrs[cur])
                        if (!item.inner) { // 不处理内部属性
                            if (item.hasOwnProperty('default')) {
                                if (item.type === Function) {
                                    item.value = item.default
                                } else {
                                    item.value = typeof item.default === 'function' ? item.default() : item.default
                                }
                            } else {
                                item.value = ''
                            }

                            delete item.default
                            attrs[cur] = item
                        }
                        return attrs
                    }, attrs)
                    tagConfigMap[tag] = {
                        tag,
                        config: {
                            type,
                            attrs,
                            events: [],
                            methods: {}
                        }
                    }
                })
                return tagConfigMap
            },
            transAtomConfig (forms) {
                const atomConfig = forms.map(item => {
                    const config = tools.deepClone(item.config)
                    Object.keys(config.attrs).forEach(key => {
                        if (typeof config.attrs[key].value === 'function') {
                            config.attrs[key] = config.attrs[key].value
                        } else {
                            config.attrs[key] = tools.deepClone(config.attrs[key].value)
                        }
                    })
                    return config
                })
                this.atomConfig = atomConfig
            },
            updateForm (formList) {
                this.forms = formList
            },
            editForm (form) {
                this.showAtomSetting = true
                this.editingForm = form
            },
            formSorted (formList) {
                this.forms = formList
            },
            refreshFormPanel () {
                this.hideFormPanel = true
                setTimeout(() => {
                    this.hideFormPanel = false
                }, 0)
            },
            atomEditError (error) {
                this.atomStringError = error
            },
            atomConfigUpdate (val) {
                const formConfig = tools.deepClone(val)
                const forms = formConfig.map((item, index) => {
                    const tagName = item.type.split('_').map(tp => tp.replace(/^\S/, s => s.toUpperCase())).join('')
                    const tag = `Tag${tagName}`
                    const config = tools.deepClone(this.tags[tag].config)
                    config.tag_code = item.tag_code

                    if (item.hasOwnProperty('events')) {
                        config.events = item.events
                    }
                    if (item.hasOwnProperty('methods')) {
                        config.methods = item.methods
                    }
                    Object.keys(config.attrs).forEach(key => {
                        if (item.attrs.hasOwnProperty(key)) {
                            const attr = config.attrs[key]
                            attr.value = item.attrs[key]
                        }
                    })
                    return {
                        config,
                        tag
                    }
                })
                const isFormChanged = !tools.isDataEqual(this.forms, forms)
                this.forms = forms
                if (isFormChanged) {
                    this.refreshFormPanel()
                }
            },
            apiCodeUpdate (val) {
                this.apiCodeStr = val
            },
            async onDownloadClick () {
                if (this.atomStringError) {
                    return
                }
                try {
                    await this.$refs.configPanel.validate()
                    const zip = new JSZip()
                    const formConfigContent = `(function(){\n$.${this.atomName}=${this.atomConfigStr}})()`
                    zip.file(`${this.atomName}.js`, formConfigContent)
                    zip.file(`${this.atomName}.py`, this.apiCodeStr)
                    zip.generateAsync({ type: 'blob' }).then(content => {
                        saveAs(content, 'bk_pulgin_code.zip')
                    })
                } catch (error) {
                    console.log(error)
                }
            },
            onOpenPreviewMode () {
                this.isPreviewMode = true
                this.previewDialogShow = true
                this.renderFormData = {}
            },
            onPreviewClose () {
                this.isPreviewMode = false
                this.previewDialogShow = false
            },
            handleFormFile (e, type) {
                const self = this
                this.fileUploading = true
                const files = e.target.files
                const fileReader = new FileReader()

                fileReader.readAsText(files[0], 'utf-8')
                fileReader.onload = function () {
                    self.fileUploading = false
                    self.showUploadDialog = false
                    self.isPreviewMode = false
                    if (type === 'formCode') {
                        self.atomConfigStr = fileReader.result
                        self.$refs.configPanel.atomConfigUpdate(fileReader.result)
                    } else {
                        self.apiCodeUpdate(fileReader.result)
                    }
                    self.$refs.configPanel.scroll(type)
                }
            },
            async onSaveAtomSetting () {
                const form = await this.$refs.atomSetting.validate()
                if (form) {
                    this.closeSettingPanel()
                    const index = this.forms.findIndex(item => item.config.tag_code === this.editingForm.config.tag_code)
                    this.forms.splice(index, 1, form)
                    this.refreshFormPanel()
                }
            },
            closeSettingPanel () {
                this.showAtomSetting = false
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';

    .atomdev-page {
        min-width: 1320px;
        height: 100%;
    }
    .page-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 20px;
        height: 50px;
        border-bottom: 1px solid #dde4eb;
        .operate-area > button {
            margin-left: 6px;
        }
    }
    .atom-edit-wrapper {
        display: flex;
        justify-content: space-around;
        height: calc(100% - 50px);
    }
    .tag-panel-col {
        width: 56px;
        height: 100%;
        border-right: 1px solid #dde4eb;
    }
    .form-panel-col {
        width: 750px;
        height: 100%;
    }
    .config-panel-col {
        width: calc(100% - 806px);
        height: 100%;
        background: #ffffff;
        border-left: 1px solid #dde4eb;
    }
    .slider-footer {
        padding: 0 20px;
    }
    .preview-panel {
        margin: 0 auto;
        width: 650px;
        height: 100%;
        background: #ffffff;
        overflow-y: auto;
        @include scrollbar;
        .render-form {
            padding: 30px 80px 20px 20px;
        }
    }
    .error-message {
        padding: 10px;
        color: #ff5656;
        word-break: break-all;
    }
    .import-wrapper {
        text-align: center;
        .import-code {
            display: inline-block;
            margin: 0 4px;
            width: 88px;
            height: 32px;
            border: none;
        }
    }
</style>
