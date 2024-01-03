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
        <bk-alert type="warning" closable :close-text="$t('我知道了')" v-if="globalVarLength">
            <template slot="title">
                <i18n v-if="render" tag="div" path="tagRenderCodeEditorTips">
                    <span class="strong">{{ $t('即将废弃') }}</span>
                    <span class="strong num">{{ globalVarLength }}</span>
                </i18n>
                <i18n v-else tag="div" path="tagCodeEditorTips">
                    <span class="strong">{{ $t('不再支持') }}</span>
                    <span class="strong num">{{ globalVarLength }}</span>
                </i18n>
            </template>
        </bk-alert>
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
    import { mapState } from 'vuex'
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
        variable_render: {
            type: Boolean,
            default: false,
            desc: 'Variable render'
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
                languages: ['javascript', 'typescript', 'json', 'python', 'shell'],
                decorationsMap: {},
                globalVarLength: 0
            }
        },
        computed: {
            ...mapState({
                'internalVariable': state => state.template.internalVariable
            }),
            constantArr: {
                get () {
                    let KeyList = []
                    if (this.constants) {
                        KeyList = [...Object.keys(this.constants)]
                    }
                    if (this.internalVariable) {
                        KeyList = [...KeyList, ...Object.keys(this.internalVariable)]
                    }
                    return KeyList
                },
                set (val) {
                    this.varList = val
                }
            },
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
            }
        },
        mounted () {
            this.setVariableTag(this.value)
        },
        methods: {
            contentUpdate (val) {
                if (this.hook) return
                this.updateForm(val)
                this.setVariableTag(val, true)
            },
            // 变量tag设置
            setVariableTag (value, valueUpdate) {
                const { attrs } = this.scheme
                if (attrs.variable_render !== false) return
                const regex = /\${[a-zA-Z_]\w*}/
                const rows = value.split('\n')
                // 获取光标所在行
                const { monacoInstance } = this.$refs.tagCodeEditor?.$refs.codeEditor || {}
                const { lineNumber } = monacoInstance?.getPosition() || {}
                if (regex.test(value)) {
                    const matchMap = rows.reduce((acc, cur, idx) => {
                        const variables = cur.match(/\${[a-zA-Z_]\w*}/g) || []
                        const matchList = variables.filter(item => this.constantArr.includes(item))
                        if (matchList.length) {
                            acc[idx + 1] = matchList
                        }
                        return acc
                    }, {})
                    // 脚本内容存在全局变量
                    this.globalVarLength = Object.values(matchMap).flat().length
                    // 数据更新处理逻辑
                    if (valueUpdate) {
                        // 清空本行所有变量色块
                        if (this.decorationsMap[lineNumber]) {
                            this.decorationsMap[lineNumber].forEach(decorations => {
                                monacoInstance.deltaDecorations(
                                    [...decorations],
                                    []
                                )
                            })
                            delete this.decorationsMap[lineNumber]
                        }
                        // 检查光标位置，如果光标没有定位在全局变量所在行，则不进行后续处理
                        if (!matchMap[lineNumber]) return
                    }
                    Object.keys(matchMap).forEach(idx => {
                        let start = 0 // 兼容一行中有多个相同的变量
                        matchMap[idx].forEach(variable => {
                            const startNumber = rows[idx - 1].indexOf(variable, start) + 1
                            const endNumber = startNumber + variable.length
                            start = endNumber
                            const decorations = monacoInstance.deltaDecorations(
                                [],
                                [
                                    {
                                        range: new monaco.Range(idx, startNumber, idx, endNumber),
                                        options: {
                                            inlineClassName: 'variable-tag'
                                        }
                                    }
                                ]
                            )
                            if (idx in this.decorationsMap) {
                                this.decorationsMap[idx].push(decorations)
                            } else {
                                this.decorationsMap[idx] = [decorations]
                            }
                        })
                    })
                } else {
                    Object.keys(this.decorationsMap).forEach(key => {
                        this.decorationsMap[key].forEach(decorations => {
                            monacoInstance.deltaDecorations(
                                [...decorations],
                                []
                            )
                        })
                    })
                    this.decorationsMap = {}
                    this.globalVarLength = 0
                }
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
        .bk-alert {
            .bk-alert-title {
                .strong {
                    color: #ff9c01;
                }
                .num {
                    font-weight: 700;
                }
            }
            /deep/.close-text {
                color: #3a84ff;
            }
        }
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
                color: #ffe8c3;
                background: #76654b;
            }
        }
    }
</style>
