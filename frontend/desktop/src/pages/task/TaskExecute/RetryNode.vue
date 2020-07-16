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
    <div class="retry-node-container" v-bkloading="{ isLoading: loading, opacity: 1 }">
        <div class="edit-wrapper">
            <RenderForm
                ref="renderForm"
                v-if="!isEmptyParams"
                :scheme="renderConfig"
                :form-option="renderOption"
                v-model="renderData">
            </RenderForm>
            <NoData v-else></NoData>
        </div>
        <div class="action-wrapper">
            <bk-button theme="primary" class="first-btn" :loading="retrying" @click="onRetryTask">{{ $t('确定') }}</bk-button>
            <bk-button theme="default" @click="onCancelRetry">{{ $t('取消') }}</bk-button>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
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
                loading: true,
                retrying: false,
                bkMessageInstance: null,
                nodeInfo: {},
                renderOption: {
                    showGroup: false,
                    showLabel: true,
                    showHook: false
                },
                renderConfig: [],
                renderData: {}
            }
        },
        computed: {
            ...mapState({
                'atomFormConfig': state => state.atomForm.config
            }),
            isEmptyParams () {
                return this.renderConfig.length === 0
            }
        },
        mounted () {
            this.loadNodeInfo()
        },
        methods: {
            ...mapActions('task/', [
                'getNodeActInfo',
                'instanceRetry'
            ]),
            ...mapActions('atomForm/', [
                'loadAtomConfig'
            ]),
            async loadNodeInfo () {
                this.loading = true
                try {
                    const version = this.nodeDetailConfig.version
                    this.nodeInfo = await this.getNodeActInfo(this.nodeDetailConfig)
                    this.renderConfig = await this.getNodeConfig(this.nodeDetailConfig.component_code, version)
                    if (this.nodeInfo.result) {
                        if (this.nodeInfo) {
                            for (const key in this.nodeInfo.data.inputs) {
                                this.$set(this.renderData, key, this.nodeInfo.data.inputs[key])
                            }
                        }
                    } else {
                        errorHandler(this.nodeInfo, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.loading = false
                }
            },
            async getNodeConfig (type, version) {
                if (atomFilter.isConfigExists(type, version, this.atomFormConfig)) {
                    return this.atomFormConfig[type][version]
                } else {
                    try {
                        await this.loadAtomConfig({ atom: type, version })
                        return this.atomFormConfig[type][version]
                    } catch (e) {
                        errorHandler(e, this)
                    }
                }
            },
            async onRetryTask () {
                let formvalid = true
                if (this.$refs.renderForm) {
                    formvalid = this.$refs.renderForm.validate()
                }
                if (!formvalid || this.retrying) return

                const { instance_id, component_code, node_id } = this.nodeDetailConfig
                const data = {
                    instance_id,
                    node_id,
                    component_code,
                    inputs: JSON.stringify(this.renderData)
                }
                this.retrying = true
                try {
                    const res = await this.instanceRetry(data)
                    if (res.result) {
                        this.$bkMessage({
                            message: i18n.t('重试成功'),
                            theme: 'success'
                        })
                        this.$emit('retrySuccess', node_id)
                    } else {
                        errorHandler(res, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
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
        overflow: hidden;
        .edit-wrapper {
            padding: 20px 20px 0;
            height: calc(100% - 60px);
            overflow-y: auto;
            @include scrollbar;
        }
        .action-wrapper {
            margin-top: 30px;
            padding-left: 55px;
            height: 60px;
            line-height: 60px;
            border-top: 1px solid $commonBorderColor;
            .first-btn{
                margin-right: 12px;
            }
        }
    }
</style>
