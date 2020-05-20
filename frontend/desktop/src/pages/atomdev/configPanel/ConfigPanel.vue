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
    <div class="config-panel" ref="configPanel">
        <div class="atom-name">
            <bk-form
                ref="atomConfig"
                class="config-section"
                form-type="vertical"
                :label-width="100"
                :model="{ name }">
                <bk-form-item
                    property="name"
                    style="max-width: 536px"
                    :label="$t('插件名称')"
                    :required="true"
                    :rules="nameRule">
                    <bk-input v-model="name" :disabled="previewMode" @change="onNameChange"></bk-input>
                </bk-form-item>
            </bk-form>
            <div class="config-section form-config-section">
                <h3 class="title required">{{ $t('前端代码') }}</h3>
                <i class="config-edit-btn common-icon-gear" @click="showContextDialog = true"></i>
                <form-config
                    :value="atomConfigStr"
                    :read-only="previewMode"
                    @contentUpdate="atomConfigUpdate">
                </form-config>
            </div>
            <div class="config-section api-list-section">
                <h3 class="title required">{{ $t('API接口') }}</h3>
                <bk-select
                    v-model="selectedApi"
                    style="max-width: 536px"
                    searchable
                    :disabled="systemListLoading || previewMode"
                    @change="onSelectApi">
                    <bk-option-group
                        v-for="group in systemList"
                        :name="group.name"
                        :key="group.key">
                        <bk-option
                            v-for="item in group.children"
                            :key="item.name"
                            :id="item.name"
                            :name="item.label">
                        </bk-option>
                    </bk-option-group>
                </bk-select>
            </div>
            <div class="config-section api-config-section">
                <h3 class="title required">{{ $t('后台代码') }}</h3>
                <form-config
                    language="python"
                    :value="apiCodeStr"
                    :read-only="previewMode"
                    @contentUpdate="apiCodeUpdate">
                </form-config>
            </div>
        </div>
        <bk-dialog
            v-model="showContextDialog"
            header-position="left"
            :width="600"
            :mask-close="false"
            :title="`context${$t('配置')}`"
            :auto-close="false"
            @confirm="onContextConfirm"
            @cancel="onContextCancel">
            <context-edit style="max-width: 536px" ref="contextEdit" :value="contextValue"></context-edit>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import serializeObj from '@/utils/serializeObj.js'
    import FormConfig from './FormConfig.vue'
    import ContextEdit from './ContextEdit.vue'
    import validator from '../atomConfigSchema.js'

    const PROJECT_DEFAULT = {
        id: 1,
        bk_biz_id: 2,
        from_cmdb: true
    }

    const SITE_URL = $.context.site_url

    export default {
        name: 'ConfigPanel',
        components: {
            FormConfig,
            ContextEdit
        },
        props: {
            atomConfigStr: {
                type: String,
                default: ''
            },
            apiCodeStr: {
                type: String,
                default: ''
            },
            atomName: {
                type: String,
                default: ''
            },
            previewMode: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                name: '',
                selectedApi: '',
                systemList: [],
                systemListLoading: false,
                componentList: [],
                apiCodeLoading: false,
                showContextDialog: false,
                contextValue: {
                    project: serializeObj({ ...PROJECT_DEFAULT }, { space: 0 }),
                    siteUrl: SITE_URL
                },
                nameRule: [
                    {
                        required: true,
                        message: i18n.t('必填项'),
                        trigger: 'blur'
                    },
                    {
                        max: 100,
                        message: i18n.t('不能多于100个字符'),
                        trigger: 'blur'
                    },
                    {
                        regex: /^[A-Za-z_][a-zA-Z0-9_]*/,
                        message: i18n.t('请输入正确的插件名称，名称由字母、数字、下划线组成，且不能以数字开头'),
                        trigger: 'blur'
                    }
                ]
            }
        },
        watch: {
            atomName (val) {
                this.name = val
            }
        },
        created () {
            this.getSystemList()
        },
        methods: {
            ...mapActions('atomDev/', [
                'loadApiList',
                'loadApiComponent',
                'loadApiPluginCode'
            ]),
            async getSystemList () {
                try {
                    this.systemListLoading = true
                    const res = await this.loadApiList()
                    if (res.result) {
                        const componentRes = await this.loadApiComponent({ name: res.data.map(item => item.name) })
                        const systemList = []
                        if (componentRes.result) {
                            this.componentList = componentRes.data
                            componentRes.data.forEach(item => {
                                let system = systemList.find(sys => sys.id === item.system_id)
                                if (system) {
                                    system.children.push(item)
                                } else {
                                    system = {
                                        id: item.system_id,
                                        name: item.system_name,
                                        children: [item]
                                    }
                                    systemList.push(system)
                                }
                            })
                        }
                        this.systemList = systemList
                    } else {
                        errorHandler(res, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.systemListLoading = false
                }
            },
            async getApiCode (comp) {
                try {
                    this.apiCodeLoading = true
                    const res = await this.loadApiPluginCode({
                        system: comp.system_name,
                        component: comp.name
                    })
                    if (res.result) {
                        const apiCodeStr = res.data
                        this.apiCodeUpdate(apiCodeStr)
                    } else {
                        errorHandler(res, this)
                    }
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.apiCodeLoading = false
                }
            },
            onNameChange (val) {
                this.$emit('onNameChange', val)
            },
            atomConfigUpdate (val) {
                if (val.trim() !== '') {
                    let value = []
                    try {
                        value = eval(`(${val})`)
                    } catch (error) {
                        console.log(error)
                        this.$emit('atomEditError', error)
                        return
                    }
                    const formTagCodeList = []
                    let tagCodeRepeat = false
                    const validateResult = value.every(item => {
                        if (formTagCodeList.includes(item.tag_code)) {
                            tagCodeRepeat = true
                            this.$emit('atomEditError', i18n.t('单个标准插件里表单项 tag_code 不能重复'))
                        } else {
                            formTagCodeList.push(item.tag_code)
                        }
                        const result = validator(item)
                        if (!result) {
                            const error = validator.errors[0]
                            console.error(error)
                            this.$emit('atomEditError', `${error.dataPath} ${error.keyword} ${error.message}`)
                        }
                        return !tagCodeRepeat && result
                    })
                    if (validateResult) {
                        this.$emit('atomEditError', '')
                        this.$emit('atomConfigUpdate', value)
                    }
                } else {
                    this.$emit('atomEditError', '')
                    this.$emit('atomConfigUpdate', [])
                }
            },
            apiCodeUpdate (val) {
                this.$emit('apiCodeUpdate', val)
            },
            onSelectApi (val, options) {
                this.selectedApi = val
                const comp = this.componentList.find(item => item.name === val)
                this.getApiCode(comp)
            },
            validate () {
                return this.$refs.atomConfig.validate()
            },
            async onContextConfirm () {
                const result = await this.$refs.contextEdit.validate()
                if (result) {
                    this.showContextDialog = false
                    this.contextValue = this.$refs.contextEdit.getValue()
                }
            },
            onContextCancel () {
                this.$refs.contextEdit.resetValue(this.contextValue)
                this.$nextTick(() => {
                    this.$refs.contextEdit.validate()
                })
            },
            scroll (type = 'formCode') {
                if (type === 'formCode') {
                    this.$refs.configPanel.scrollTop = 0
                } else {
                    this.$refs.configPanel.scrollTop = this.$refs.configPanel.scrollHeight
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';

    .config-panel {
        position: relative;
        padding: 20px;
        height: 100%;
        overflow-y: auto;
        @include scrollbar;

        /deep/ .bk-form {
            .bk-label {
                text-align: left;
                color: #63656e;
            }
        }
        .config-section {
            position: relative;
            margin-bottom: 24px;
            & > .title {
                position: relative;
                margin: 0 0 4px;
                font-size: 14px;
                font-weight: normal;
                color: #63656e;
                &.required:after {
                    content: "*";
                    color: #ff5656;
                    position: relative;
                    margin: 2px -7px 0 2px;
                    display: inline-block;
                    vertical-align: middle;
                }
            }
            .config-edit-btn {
                position: absolute;
                top: 4px;
                right: 0;
                color: #7a8193;
                cursor: pointer;
                &:hover {
                    color: #3a84ff;
                }
            }
        }
    }
</style>
