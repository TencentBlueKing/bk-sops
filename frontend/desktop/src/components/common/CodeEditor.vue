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
    <section class="code-editor"></section>
</template>
<script>
    import * as monaco from 'monaco-editor'

    const DEFAULT_OPTIONS = {
        language: 'javascript',
        theme: 'vs-dark',
        automaticLayout: true,
        minimap: {
            enabled: false
        },
        wordWrap: 'on',
        wrappingIndent: 'same'
    }
    export default {
        name: 'CodeEditor',
        props: {
            value: {
                type: String,
                default: ''
            },
            options: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            const editorOptions = Object.assign({}, DEFAULT_OPTIONS, this.options, { value: this.value })
            return {
                editorOptions,
                monacoInstance: null
            }
        },
        watch: {
            value (val) {
                const valInEditor = this.monacoInstance.getValue()
                if (val !== valInEditor) {
                    this.monacoInstance.setValue(val)
                }
            },
            options: {
                deep: true,
                handler (val) {
                    this.editorOptions = Object.assign({}, DEFAULT_OPTIONS, val, { value: this.value })
                    this.updateOptions()
                }
            }
        },
        mounted () {
            this.initIntance()
        },
        beforeDestroy () {
            if (this.monacoInstance) {
                this.monacoInstance.dispose()
            }
        },
        methods: {
            initIntance () {
                this.monacoInstance = monaco.editor.create(this.$el, this.editorOptions)
                const model = this.monacoInstance.getModel()
                model.onDidChangeContent(event => {
                    const value = this.monacoInstance.getValue()
                    this.$emit('input', value)
                })
                this.monacoInstance.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S, () => {
                    const value = this.monacoInstance.getValue()
                    this.$emit('saveContent', value)
                })
            },
            updateOptions () {
                this.monacoInstance.updateOptions(this.editorOptions)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .code-editor {
        height: 100%;
    }
</style>
