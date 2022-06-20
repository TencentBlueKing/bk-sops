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
    <div
        class="modify-params-container"
        v-bkloading="{ isLoading: loading, opacity: 1, zIndex: 100 }"
        @click="e => e.stopPropagation()">
        <div v-if="state !== 'CREATED'" class="panel-notice-task-run">
            <p>
                <i class="common-icon-info ui-notice"></i>
                {{ paramsCanBeModify ? $t('已开始执行的任务，修改参数值仅对还未执行的步骤生效') : $t('已执行完毕的任务不能修改参数') }}
            </p>
        </div>
        <div :class="['edit-wrapper', { 'cancel-check': state !== 'CREATED' }]">
            <TaskParamEdit
                v-if="!isParamsEmpty"
                ref="TaskParamEdit"
                :pre-mako-disabled="(!paramsCanBeModify || state === 'CREATED') ? false : true"
                :constants="constants"
                :editable="paramsCanBeModify"
                @onChangeConfigLoading="onChangeConfigLoading">
            </TaskParamEdit>
            <NoData v-else></NoData>
        </div>
        <div class="action-wrapper">
            <div v-if="!isParamsEmpty && paramsCanBeModify">
                <bk-button
                    theme="primary"
                    :class="{
                        'btn-permission-disable': !hasSavePermission
                    }"
                    :loading="pending"
                    v-cursor="{ active: !hasSavePermission }"
                    data-test-id="taskExecute_form_saveModifyParamsBtn"
                    @click="onModifyParams">
                    {{ $t('保存') }}
                </bk-button>
                <bk-button theme="default" data-test-id="taskExecute_form_cancelBtn" @click="onCancelRetry">{{ $t('取消') }}</bk-button>
            </div>

            <bk-button v-else theme="default" data-test-id="taskExecute_form_closeBtn" @click="onCancelRetry">{{ $t('关闭') }}</bk-button>
        </div>

    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import bus from '@/utils/bus.js'
    import { mapState, mapActions } from 'vuex'
    import permission from '@/mixins/permission.js'
    import NoData from '@/components/common/base/NoData.vue'
    import TaskParamEdit from '../TaskParamEdit.vue'

    export default {
        name: 'ModifyParams',
        components: {
            TaskParamEdit,
            NoData
        },
        mixins: [permission],
        props: ['state', 'instanceName', 'instance_id', 'paramsCanBeModify', 'instanceActions'],
        data () {
            return {
                bkMessageInstance: null,
                constants: [],
                cntLoading: true, // 全局变量加载
                configLoading: true, // 变量配置项加载
                pending: false, // 提交修改中
                remoteData: '' // 文本值下拉框变量远程数据源
            }
        },
        computed: {
            ...mapState('project', {
                'projectId': state => state.project_id,
                'projectName': state => state.projectName
            }),
            isParamsEmpty () {
                return !Object.keys(this.constants).length
            },
            hasSavePermission () {
                return this.hasPermission(['task_edit'], this.instanceActions)
            },
            loading () {
                return this.isParamsEmpty ? this.cntLoading : (this.cntLoading || this.configLoading)
            }
        },
        created () {
            bus.$on('tagRemoteLoaded', data => {
                this.remoteData = { ...data }
            })
            this.getTaskData()
        },
        methods: {
            ...mapActions('task/', [
                'getTaskInstanceData',
                'instanceModifyParams'
            ]),
            async getTaskData () {
                this.cntLoading = true
                try {
                    const instanceData = await this.getTaskInstanceData(this.instance_id)
                    const pipelineData = JSON.parse(instanceData.pipeline_tree)
                    const constants = {}
                    Object.keys(pipelineData.constants).forEach(key => {
                        const cnt = pipelineData.constants[key]
                        if (cnt.show_type === 'show') {
                            constants[key] = cnt
                        }
                    })
                    this.constants = constants
                } catch (e) {
                    console.log(e)
                } finally {
                    this.cntLoading = false
                }
            },
            judgeDataEqual () {
                if (!this.paramsCanBeModify || !this.$refs.TaskParamEdit) {
                    return true
                }
                return this.$refs.TaskParamEdit.judgeDataEqual()
            },
            async onModifyParams () {
                if (!this.hasSavePermission) {
                    const resourceData = {
                        task: [{
                            id: this.instance_id,
                            name: this.instanceName
                        }],
                        project: [{
                            id: this.projectId,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission(['task_edit'], this.instanceActions, resourceData)
                    return
                }

                if (this.pending) {
                    return
                }
                const paramEditComp = this.$refs.TaskParamEdit
                const formData = {}
                const metaConstants = {}
                let formValid = true
                if (paramEditComp) {
                    formValid = paramEditComp.validate()
                    if (!formValid) return false
                    const variables = await paramEditComp.getVariableData()
                    for (const key in variables) {
                        const { value, pre_render_mako } = variables[key]
                        // 过滤掉预渲染类型的变量
                        if (pre_render_mako !== true) {
                            formData[key] = value
                        }
                    }
                    // 远程数据源模式下，需要传meta_constants在text_value_select变量的meta.value
                    if (Object.keys(this.remoteData).length) {
                        Object.values(variables).forEach(item => {
                            if (item.custom_type === 'text_value_select' && this.remoteData[item.key]) {
                                const metaValue = item.meta.value
                                metaConstants[item.key] = metaValue
                            }
                        })
                    }
                }
                const data = {
                    instance_id: this.instance_id,
                    constants: formData,
                    meta_constants: Object.keys(metaConstants).length ? metaConstants : undefined
                }
                try {
                    this.pending = true
                    const res = await this.instanceModifyParams(data)
                    if (res.result) {
                        this.$bkMessage({
                            message: i18n.t('参数修改成功'),
                            theme: 'success'
                        })
                        this.$emit('packUp')
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending = false
                }
            },
            onChangeConfigLoading (val) {
                this.configLoading = val
            },
            onCancelRetry () {
                this.$emit('packUp')
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/config.scss';
    @import '@/scss/mixins/scrollbar.scss';
    .modify-params-container {
        position: relative;
        height: 100%;
        overflow: hidden;
        .panel-notice-task-run {
            margin: 20px 20px 10px 20px;
            padding: 0 10px;
            font-size: 12px;
            line-height: 36px;
            color: #63656e;
            background: #f0f8ff;
            border: 1px solid #c5daff;
            box-shadow: 0 2px 4px 0 #e1e8f4;
            border-radius: 2px;
            .ui-notice {
                font-size: 16px;
                margin-right: 6px;
                color: $blueDefault;
            }
        }
        .edit-wrapper {
            padding: 20px;
            height: calc(100% - 60px);
            overflow-y: auto;
            @include scrollbar;
        }
        .cancel-check {
            height: calc(100% - 126px);
        }
        .action-wrapper {
            padding-left: 20px;
            height: 60px;
            line-height: 60px;
            border-top: 1px solid $commonBorderColor;
        }
    }
</style>
