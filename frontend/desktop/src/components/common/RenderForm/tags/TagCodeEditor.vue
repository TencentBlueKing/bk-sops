/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="tag-code-editor">
        <div class="control-header" v-if="showLanguageSwitch">
            <div class="language-select">
                <bk-select
                    v-model="language"
                    :clearable="false"
                    size="mini"
                    style="width: 120px;"
                    @change="onLanguageChange">
                    <bk-option
                        v-for="item in languages"
                        :key="item"
                        :name="item"
                        :id="item">
                    </bk-option>
                </bk-select>
            </div>
        </div>
        <div
            :style="{ height: height }"
            class="code-editor-wrap">
            <full-code-editor
                v-if="!editorReload"
                ref="tagCodeEditor"
                :value="value"
                :options="{
                    language,
                    readOnly: disabled,
                    minimap: {
                        enabled: showMiniMap
                    }
                }"
                @input="contentUpdate">
            </full-code-editor>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { getFormMixins } from '../formMixins.js'
    import FullCodeEditor from '@/components/common/FullCodeEditor.vue'
    import * as monaco from 'monaco-editor'
    export const attrs = {
        language: {
            type: String,
            default: 'python',
            desc: 'Code editor language'
        },
        height: {
            type: String,
            default: '100px',
            desc: 'The editor height'
        },
        showMiniMap: {
            type: Boolean,
            default: false,
            desc: 'Show editor mini code map'
        },
        showLanguageSwitch: {
            type: Boolean,
            default: true,
            desc: 'Show editor language switch'
        },
        readOnly: {
            type: Boolean,
            default: false,
            desc: 'The editor code is read-only'
        },
        value: {
            type: String,
            default: ''
        }
    }
    export default {
        name: 'TagCodeEditor',
        components: {
            FullCodeEditor
        },
        mixins: [getFormMixins(attrs)],
        data () {
            return {
                editorReload: false,
                languages: ['javascript', 'typescript', 'json', 'python', 'shell']
            }
        },
        computed: {
            disabled () {
                return !this.editable || this.readOnly
            }
        },
        watch: {
            editable () {
                this.onLanguageChange()
            },
            readOnly () {
                this.onLanguageChange()
            },
            value: {
                handler (val) {
                    console.log(val)
                },
                deep: true
            }
        },
        mounted () {
            // 不是变量免渲染则有限判断脚本内容是否包含全局变量
            if (this.render) {
                const regex = /\${[a-zA-Z_]\w*}/
                if (regex.test(this.value)) {
                    const rows = this.value.split('\n')
                    const matchIndex = rows.reduce((acc, cur, idx) => {
                        if (regex.test(cur)) {
                            acc.push(idx + 1)
                        }
                        return acc
                    }, [])
                    const { monacoInstance } = this.$refs.tagCodeEditor?.$refs.codeEditor || {}
                    matchIndex.forEach(index => {
                        const variable = rows[index - 1].match(regex)[0]
                        const startNumber = rows[index - 1].split(variable)[0].length || 1
                        const endNumber = startNumber + variable.length
                        monacoInstance.deltaDecorations(
                            [],
                            [
                                {
                                    range: new monaco.Range(index, startNumber, index, endNumber),
                                    options: {
                                        inlineClassName: 'variable-tag',
                                        hoverMessage: { isTrusted: true, supportHtml: true, value: '<p>我是猪</p><p>你也是猪</p>' }
                                    }
                                }
                            ]
                        )
                    })
                }
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
                this.editorReload = true
                this.$nextTick(() => {
                    this.editorReload = false
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
            .language-select {
                float: right;
            }
        }
        .code-editor-wrap {
            position: relative;
            /deep/.view-lines .variable-tag {
                display: inline-block;
                color: red;
                background: #fff2e8;
            }
        }
    }
</style>
