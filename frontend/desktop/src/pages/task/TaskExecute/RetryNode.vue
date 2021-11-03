/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="retry-node-container" v-bkloading="{ isLoading: loading, opacity: 1, zIndex: 100 }">
        <div class="edit-wrapper">
            <RenderForm
                ref="renderForm"
                v-if="!isEmptyParams && !loading"
                :scheme="renderConfig"
                :form-option="renderOption"
                v-model="renderData">
            </RenderForm>
            <NoData v-else></NoData>
        </div>
        <div class="action-wrapper">
            <bk-button theme="primary" class="confirm-btn" :loading="retrying" @click="onRetryTask">{{ $t('确定') }}</bk-button>
            <bk-button theme="default" @click="onCancelRetry">{{ $t('取消') }}</bk-button>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'
    import tools from '@/utils/tools.js'
    import NoData from '@/components/common/base/NoData.vue'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    import atomFilter from '@/utils/atomFilter.js'
    export default {
        name: 'RetryNode',
        components: {
            RenderForm,
            NoData
        },
        props: ['nodeDetailConfig'],
        data () {
            return {
                loading: false,
                retrying: false,
                bkMessageInstance: null,
                nodeInfo: {},
                renderOption: {
                    showGroup: false,
                    showLabel: true,
                    showHook: false
                },
                renderConfig: [],
                renderData: {},
                initalRenderData: {}
            }
        },
        computed: {
            ...mapState({
                'atomFormConfig': state => state.atomForm.config
            }),
            ...mapState('project', {
                project_id: state => state.project_id
            }),
            isEmptyParams () {
                return this.renderConfig.length === 0
            }
        },
        mounted () {
            if (this.nodeDetailConfig.component_code) {
                this.loadNodeInfo()
            }
        },
        methods: {
            ...mapActions('task/', [
                'getNodeActInfo',
                'instanceRetry',
                'subflowNodeRetry'
            ]),
            ...mapActions('atomForm/', [
                'loadAtomConfig',
                'loadPluginServiceDetail'
            ]),
            async loadNodeInfo () {
                this.loading = true
                try {
                    const version = this.nodeDetailConfig.version
                    this.nodeInfo = await this.getNodeActInfo(this.nodeDetailConfig)
                    await this.getNodeConfig(this.nodeDetailConfig.component_code, version)
                    if (this.nodeInfo.result) {
                        if (this.nodeInfo) {
                            for (const key in this.nodeInfo.data.inputs) {
                                this.$set(this.renderData, key, this.nodeInfo.data.inputs[key])
                            }
                            this.initalRenderData = tools.deepClone(this.renderData)
                        }
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.loading = false
                }
            },
            async getNodeConfig (type, version) {
                if (atomFilter.isConfigExists(type, version, this.atomFormConfig)) {
                    this.renderConfig = this.atomFormConfig[type][version]
                } else {
                    try {
                        // 第三方插件节点拼接输出参数
                        if (this.nodeDetailConfig.component_code === 'remote_plugin') {
                            const { inputs } = this.nodeInfo.data
                            const pluginVersion = inputs && inputs.plugin_version
                            const pluginCode = inputs && inputs.plugin_code
                            const resp = await this.loadPluginServiceDetail({
                                plugin_code: pluginCode,
                                plugin_version: pluginVersion,
                                with_app_detail: true
                            })
                            if (!resp.result) return
                            
                            // 设置host
                            const { origin } = window.location
                            const hostUrl = `${origin + window.SITE_URL}plugin_service/data_api/${pluginCode}/`
                            $.context.bk_plugin_api_host[pluginCode] = hostUrl
                            // 输入参数
                            const renderFrom = resp.data.forms.renderform
                            /* eslint-disable-next-line */
                            eval(renderFrom)
                            const config = $.atoms[pluginCode]
                            this.renderConfig = config || []
                        } else {
                            await this.loadAtomConfig({ atom: type, version, project_id: this.project_id })
                            this.renderConfig = this.atomFormConfig[type][version]
                        }
                    } catch (e) {
                        console.log(e)
                    }
                }
            },
            judgeDataEqual () {
                return tools.isDataEqual(this.initalRenderData, this.renderData)
            },
            async onRetryTask () {
                let formvalid = true
                if (this.$refs.renderForm) {
                    formvalid = this.$refs.renderForm.validate()
                }
                if (!formvalid || this.retrying) return false

                const { instance_id, component_code, node_id } = this.nodeDetailConfig
                this.retrying = true
                try {
                    let res
                    if (this.nodeDetailConfig.component_code) {
                        const data = {
                            instance_id,
                            node_id,
                            component_code,
                            inputs: this.renderData
                        }
                        res = await this.instanceRetry(data)
                    } else {
                        res = await this.subflowNodeRetry({ instance_id, node_id })
                    }
                    if (res.result) {
                        this.$bkMessage({
                            message: i18n.t('重试成功'),
                            theme: 'success'
                        })
                        this.$emit('retrySuccess', node_id)
                        return true
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.retrying = false
                }
            },
            onCancelRetry () {
                const { node_id } = this.nodeDetailConfig
                this.$emit('retryCancel', node_id)
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/config.scss';
    @import '@/scss/mixins/scrollbar.scss';
    .retry-node-container {
        position: relative;
        height: 100%;
        overflow: hidden;
        .edit-wrapper {
            padding: 20px 20px 0;
            height: calc(100% - 60px);
            overflow-y: auto;
            @include scrollbar;
        }
        .action-wrapper {
            padding-left: 20px;
            height: 60px;
            line-height: 60px;
            border-top: 1px solid $commonBorderColor;
            .confirm-btn{
                margin-right: 12px;
            }
        }
    }
</style>
