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
    <div class="modify-time-container" v-bkloading="{ isLoading: loading, opacity: 1 }">
        <div class="panel-title">
            <h3>{{ i18n.reset_timer }}</h3>
        </div>
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
        <div class="action-wrapper" v-if="!isEmptyParams">
            <bk-button theme="success" @click="onModifyTime">{{ i18n.confirm }}</bk-button>
            <bk-button theme="default" @click="onCancelRetry">{{ i18n.cancel }}</bk-button>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import NoData from '@/components/common/base/NoData.vue'
    import RenderForm from '@/components/common/RenderForm/RenderForm.vue'
    export default {
        name: 'ModifyTime',
        components: {
            RenderForm,
            NoData
        },
        props: ['nodeDetailConfig'],
        data () {
            return {
                i18n: {
                    reset_timer: gettext('修改定时时间'),
                    confirm: gettext('确定'),
                    cancel: gettext('取消')
                },
                loading: true,
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
                return Object.keys(this.renderData).length === 0
            }
        },
        mounted () {
            this.loadNodeInfo()
        },
        methods: {
            ...mapActions('task/', [
                'getNodeActDetail',
                'setSleepNode'
            ]),
            ...mapActions('atomForm/', [
                'loadAtomConfig'
            ]),
            ...mapMutations('atomForm/', [
                'setAtomConfig'
            ]),
            async loadNodeInfo () {
                this.loading = true
                try {
                    const nodeDetailRes = await this.getNodeActDetail(this.nodeDetailConfig)
                    this.renderConfig = await this.getNodeConfig(this.nodeDetailConfig.component_code)
                    this.nodeInfo = nodeDetailRes.data
                    if (nodeDetailRes.result) {
                        for (const key in this.nodeInfo.inputs) {
                            this.$set(this.renderData, key, this.nodeInfo.inputs[key])
                        }
                    } else {
                        errorHandler(nodeDetailRes, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.loading = false
                }
            },
            async getNodeConfig (type) {
                if (this.atomFormConfig[type]) {
                    return this.atomFormConfig[type]
                } else {
                    try {
                        await this.loadAtomConfig({ atomType: type })
                        this.setAtomConfig({ atomType: type, configData: $.atoms[type] })
                        return this.atomFormConfig[type]
                    } catch (e) {
                        errorHandler(e, this)
                    }
                }
            },
            async onModifyTime () {
                let formvalid = true
                if (this.$refs.renderForm) {
                    formvalid = this.$refs.renderForm.validate()
                }
                if (!formvalid) return

                const { instance_id, component_code, node_id } = this.nodeDetailConfig
                const data = {
                    instance_id,
                    node_id,
                    component_code,
                    inputs: JSON.stringify(this.renderData)
                }
                this.retrying = true
                try {
                    const res = await this.setSleepNode(data)
                    if (res.result) {
                        this.$emit('modifyTimeSuccess', node_id)
                        this.$bkMessage({
                            message: gettext('修改成功'),
                            theme: 'success'
                        })
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
                this.$emit('modifyTimeCancel', node_id)
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/config.scss';
    @import '@/scss/mixins/scrollbar.scss';
    .modify-time-container {
        position: relative;
        height: 100%;
        overflow: hidden;
        .panel-title {
            padding: 20px;
            h3 {
                margin: 0;
                font-size: 22px;
                font-weight: normal;
            }
        }
        .edit-wrapper {
            padding: 20px 20px 0;
            height: calc(100% - 140px);
            overflow-y: auto;
            @include scrollbar;
        }
        .action-wrapper {
            height: 60px;
            line-height: 60px;
            text-align: center;
            border-top: 1px solid $commonBorderColor;
        }
    }
</style>
