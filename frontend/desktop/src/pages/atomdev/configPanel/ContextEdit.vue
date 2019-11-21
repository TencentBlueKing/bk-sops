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
    <div class="context-edit">
        <bk-form
            ref="contextForm"
            form-type="vertical"
            :label-width="80"
            :model="{ project }">
            <bk-form-item
                label="project"
                property="project"
                :required="true"
                :rules="projectRule">
                <bk-input v-model="project" type="textarea" :row="5" @blur="transformProject"></bk-input>
            </bk-form-item>
            <bk-form-item label="site_url">
                <bk-input v-model="siteUrl"></bk-input>
            </bk-form-item>
        </bk-form>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import tools from '@/utils/tools.js'

    export default {
        name: 'ContextEdit',
        props: {
            value: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            const context = tools.deepClone($.context)
            return {
                context,
                project: this.value.project,
                siteUrl: this.value.siteUrl,
                projectRule: [
                    {
                        validator (val) {
                            try {
                                const obj = eval(`(${val})`)
                                return Object.prototype.toString.call(obj) === '[object Object]'
                            } catch (error) {
                                return false
                            }
                        },
                        message: gettext('请输入合法对象'),
                        trigger: 'blur'
                    }
                ],
                i18n: {
                    project: gettext('项目')
                }
            }
        },
        watch: {
            siteUrl (val) {
                $.context.site_url = val
            },
            value (val) {
                this.resetValue(val)
            }
        },
        beforeDestroy () {
            $.context = this.context
        },
        methods: {
            transformProject (val) {
                try {
                    const project = eval(`(${val})`)
                    $.context.project = project
                } catch (error) {
                    console.log(error)
                }
            },
            validate () {
                return this.$refs.contextForm.validate()
            },
            resetValue (val) {
                const { project, siteUrl } = val
                this.project = project
                this.siteUrl = siteUrl
                this.transformProject(project)
            },
            getValue () {
                return {
                    project: this.project,
                    siteUrl: this.siteUrl
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .context-edit {
        padding: 0;
    }
    /deep/ .bk-form {
        .bk-label {
            font-size: 12px;
        }
    }
</style>
