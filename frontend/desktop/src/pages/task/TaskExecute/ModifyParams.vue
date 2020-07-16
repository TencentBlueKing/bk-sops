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
    <div
        class="modify-params-container"
        v-bkloading="{ isLoading: loading, opacity: 1 }"
        @click="e => e.stopPropagation()">
        <div v-if="!paramsCanBeModify" class="panel-notice-task-run">
            <p>
                <i class="common-icon-info ui-notice"></i>
                {{ $t('已开始执行的任务不能修改参数') }}
            </p>
        </div>
        <div class="edit-wrapper">
            <TaskParamEdit
                v-if="!isParamsEmpty"
                ref="TaskParamEdit"
                :constants="constants"
                :editable="paramsCanBeModify"
                @onChangeConfigLoading="onChangeConfigLoading">
            </TaskParamEdit>
            <NoData v-else></NoData>
        </div>
        <div class="action-wrapper" v-if="!isParamsEmpty && paramsCanBeModify">
            <bk-button
                theme="primary"
                :class="{
                    'btn-permission-disable': !hasSavePermission
                }"
                v-cursor="{ active: !hasSavePermission }"
                @click="onModifyParams">
                {{ $t('保存') }}
            </bk-button>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
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
        props: ['instanceName', 'instance_id', 'paramsCanBeModify', 'instanceActions', 'instanceOperations', 'instanceResource'],
        data () {
            return {
                bkMessageInstance: null,
                constants: [],
                cntLoading: true, // 全局变量加载
                configLoading: true, // 变量配置项加载
                pending: false // 提交修改中
            }
        },
        computed: {
            isParamsEmpty () {
                return !Object.keys(this.constants).length
            },
            hasSavePermission () {
                return this.hasPermission(['edit'], this.instanceActions, this.instanceOperations)
            },
            loading () {
                return this.isParamsEmpty ? this.cntLoading : (this.cntLoading || this.configLoading)
            }
        },
        created () {
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
                    errorHandler(e, this)
                } finally {
                    this.cntLoading = false
                }
            },
            async onModifyParams () {
                if (!this.hasSavePermission) {
                    const resourceData = {
                        id: this.instance_id,
                        name: this.instanceName,
                        auth_actions: this.instanceActions
                    }
                    this.applyForPermission(['edit'], resourceData, this.instanceOperations, this.instanceResource)
                }

                if (this.pending) {
                    return
                }
                const paramEditComp = this.$refs.TaskParamEdit
                const formData = {}
                let formValid = true
                if (paramEditComp) {
                    formValid = paramEditComp.validate()
                    if (!formValid) return
                    const variables = paramEditComp.getVariableData()
                    for (const key in variables) {
                        formData[key] = variables[key].value
                    }
                }

                const data = {
                    instance_id: this.instance_id,
                    constants: JSON.stringify(formData)
                }
                try {
                    this.pending = true
                    const res = await this.instanceModifyParams(data)
                    if (res.result) {
                        this.$bkMessage({
                            message: i18n.t('参数修改成功'),
                            theme: 'success'
                        })
                    } else {
                        errorHandler(res, this)
                    }
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.pending = false
                }
            },
            onChangeConfigLoading (val) {
                this.configLoading = val
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/config.scss';
    @import '@/scss/mixins/scrollbar.scss';
    .modify-params-container {
        position: relative;
        overflow: hidden;
        .panel-notice-task-run {
            margin: 20px 20px 10px 20px;
            padding: 0 10px;
            font-size: 12px;
            line-height: 36px;
            background: $blueNavBg;
            border: 1px solid #a3c5fd;
            .ui-notice {
                margin-right: 10px;
                color: $blueDefault;
            }
        }
        .edit-wrapper {
            padding: 20px;
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
        }
    }
</style>
