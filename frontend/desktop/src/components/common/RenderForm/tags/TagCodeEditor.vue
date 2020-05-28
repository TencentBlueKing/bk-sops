/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="tag-code-editor">
        <div class="control-header" v-if="showControl">
            <div class="language-select">
                <el-select
                    v-model="language"
                    size="mini"
                    @change="onLanguageChange">
                    <el-option
                        v-for="item in languages"
                        :key="item"
                        :label="item"
                        :value="item">
                    </el-option>
                </el-select>
            </div>
        </div>
        <div
            :style="{ height: height }"
            class="code-editor-wrap">
            <code-editor
                v-if="!editorReLoad"
                ref="tagCodeEditor"
                :value="value"
                :options="{
                    language,
                    readOnly: readOnly || !formMode,
                    theme: editorTheme,
                    minimap: {
                        enabled: showMiniMap
                    }
                }"
                @changeContent="contentUpdate">
            </code-editor>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { getFormMixins } from '../formMixins.js'
    import CodeEditor from '@/components/common/CodeEditor.vue'
    export const attrs = {
        language: {
            type: String,
            default: 'python',
            desc: 'code editor language'
        },
        height: {
            type: String,
            default: '100px',
            desc: 'the editor height'
        },
        showMiniMap: {
            type: Boolean,
            default: false,
            desc: 'show editor mini code map'
        },
        showControl: {
            type: Boolean,
            default: true,
            desc: 'show editor controller'
        },
        readOnly: {
            type: Boolean,
            default: false,
            desc: 'the editor code is read-only'
        },
        value: {
            type: String,
            default: ''
        }
    }
    export default {
        name: 'TagCodeEditor',
        components: {
            CodeEditor
        },
        mixins: [getFormMixins(attrs)],
        data () {
            return {
                editorReLoad: false,
                editorTheme: 'vs-dark',
                languages: [
                    'python',
                    'shell',
                    'javascript',
                    'typescript',
                    'java',
                    'json',
                    'mysql',
                    'bat',
                    'html',
                    'markdown',
                    'php',
                    'sql'
                ]
            }
        },
        watch: {
            formMode (val) {
                this.editorTheme = val ? 'vs-dark' : 'vs'
                this.refreshEditor()
            }
        },
        methods: {
            contentUpdate (val) {
                this.updateForm(val)
            },
            onLanguageChange () {
                this.refreshEditor()
            },
            refreshEditor () {
                this.editorReLoad = true
                this.$nextTick(() => {
                    this.editorReLoad = false
                })
            }
        }
    }
</script>
<style lang="scss" scoped>
    .tag-code-editor {
        .control-header {
            width: 100%;
            height: 34px;
            margin-bottom: 2px;
        }
        .code-editor-wrap {
            position: relative;
        }
    }
</style>
