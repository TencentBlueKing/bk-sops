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
    <div class="form-config">
        <div class="code-area">
            <code-editor
                :value="value"
                :options="options"
                @changeContent="contentUpdate">
            </code-editor>
            <div class="disable-mask" v-if="readOnly"></div>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import CodeEditor from '@/components/common/CodeEditor.vue'

    export default {
        name: 'FormConfig',
        components: {
            CodeEditor
        },
        props: {
            value: {
                type: String,
                default: ''
            },
            language: {
                type: String,
                default: 'javascript'
            },
            readOnly: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                options: {
                    language: this.language,
                    readOnly: this.readOnly
                }
            }
        },
        watch: {
            language (val) {
                this.options.language = val
            },
            readOnly (val) {
                this.options.readOnly = val
            }
        },
        methods: {
            contentUpdate (val) {
                this.$emit('contentUpdate', val)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .code-area {
        position: relative;
        height: 500px;
        .disable-mask {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.2);
            z-index: 1;
        }
    }
</style>
