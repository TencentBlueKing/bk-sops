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
        <bk-alert v-if="retryNodeId" type="warning" :title="$t('若当前节点引用了任务入参，可修改参数来更新节点配置')"></bk-alert>
        <div :class="['edit-wrapper']">
            <TaskParamEdit
                v-if="!isParamsEmpty"
                ref="TaskParamEdit"
                :is-used-tip-show="(rootTaskState !== 'CREATED' && !paramsCanBeModify) ? false : true"
                :pre-mako-disabled="(paramsCanBeModify && rootTaskState === 'CREATED') ? false : true"
                :constants="constants"
                :un-used-constants="unUsedConstants"
                :editable="paramsCanBeModify && !isChildTaskFlow && editable"
                @onChangeConfigLoading="onChangeConfigLoading">
            </TaskParamEdit>
            <NoData v-else :message="$t('暂无参数')"></NoData>
        </div>
        <div class="action-wrapper">
            <div v-if="retryNodeId || (!isParamsEmpty && paramsCanBeModify)">
                <span v-bk-tooltips="{ content: $t('子任务中任务入参不允许修改'), disabled: !isChildTaskFlow }">
                    <bk-button
                        theme="primary"
                        :class="{
                            'btn-permission-disable': !hasSavePermission
                        }"
                        :loading="pending"
                        v-cursor="{ active: !hasSavePermission }"
                        data-test-id="taskExecute_form_saveModifyParamsBtn"
                        :disabled="isChildTaskFlow"
                        @click="onConfirmClick">
                        {{ confirmBtnText }}
                    </bk-button>
                </span>
                <bk-button theme="default" :disabled="pending" data-test-id="taskExecute_form_cancelBtn" @click="onCancelRetry">{{ $t('取消') }}</bk-button>
            </div>

            <bk-button v-else theme="default" data-test-id="taskExecute_form_closeBtn" @click="onCancelRetry">{{ $t('关闭') }}</bk-button>
        </div>

    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import bus from '@/utils/bus.js'
    import { mapState, mapMutations, mapActions } from 'vuex'
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
        props: [
            'state',
            'instanceName',
            'instance_id',
            'paramsCanBeModify',
            'instanceActions',
            'retryNodeId',
            'isSubCanvas'
        ],
        data () {
            return {
                bkMessageInstance: null,
                constants: [],
                cntLoading: true, // 全局变量加载
                configLoading: true, // 变量配置项加载
                pending: false, // 提交修改中
                remoteData: {}, // 文本值下拉框变量远程数据源
                isChildTaskFlow: false, // 是否为子流程任务
                constantLoading: false, // 变量是否被使用加载
                unUsedConstants: [], // 还未执行的变量
                editable: false,
                rootState: '' // 根任务状态
            }
        },
        computed: {
            ...mapState({
                'msgInstance': state => state.msgInstance
            }),
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
                return this.isParamsEmpty ? this.cntLoading : (this.cntLoading || this.configLoading || this.constantLoading)
            },
            confirmBtnText () {
                return this.retryNodeId
                    ? i18n.t('重试')
                    : this.editable
                        ? i18n.t('保存')
                        : ['CREATED', 'SUSPENDED', 'FAILED', 'PENDING_PROCESSING'].includes(this.rootTaskState)
                            ? i18n.t('去修改')
                            : i18n.t('暂停去修改')
            },
            rootTaskState () {
                return this.isSubCanvas ? this.rootState : this.state
            }
        },
        async created () {
            if (this.retryNodeId) {
                $.context.exec_env = 'NODE_RETRY'
                this.editable = true
            }
            bus.$on('tagRemoteLoaded', (code, data) => {
                this.remoteData[code] = data
            })

            if (this.isSubCanvas) {
                this.loadRootTaskState()
            }
            
            /* 暂不进行变量是否被使用判断 */
            // 先获取被使用过的变量
            // this.constantLoading = true
            // this.unUsedConstants = await this.getUnUsedConstants()
            this.getTaskData()
        },
        mounted () {
            bus.$on('onCloseErrorNotify', (data) => {
                const varRegExp = /\${[a-zA-Z_]\w*}/g
                const matchList = data.match(varRegExp) || []
                const paramEditComp = this.$refs.TaskParamEdit
                if (matchList.length && paramEditComp) {
                    matchList.forEach(key => {
                        const config = paramEditComp.renderConfig.find(item => item.tag_code === key)
                        if (!config.attrs) {
                            config.attrs = {}
                        }
                        config.attrs['disabled'] = true
                        config.attrs['used_tip'] = i18n.t('参数已被使用，不可修改')
                    })
                    paramEditComp.randomKey = new Date().getTime()
                }
            })
            // 清理任务暂停/参数修改后继续执行 msg信息
            this.msgInstance && this.msgInstance.close()
        },
        beforeDestroy () {
            $.context.exec_env = ''
        },
        methods: {
            ...mapActions('task/', [
                'getInstanceStatus',
                'getTaskInstanceData',
                'instanceModifyParams',
                'getTaskUsedConstants',
                'instancePause',
                'instanceResume'
            ]),
            ...mapMutations([
                'setMsgInstance'
            ]),
            async loadRootTaskState () {
                try {
                    const resp = await this.getInstanceStatus({
                        project_id: this.projectId,
                        instance_id: this.instance_id
                    })
                    if (resp.result) {
                        this.rootState = resp.data.state
                    }
                } catch (error) {
                    console.warn(error)
                }
            },
            async getTaskData () {
                this.cntLoading = true
                try {
                    const instanceData = await this.getTaskInstanceData(this.instance_id)
                    const pipelineData = JSON.parse(instanceData.pipeline_tree)
                    const constants = {}
                    const { has_key = false, keys_in_constants_parameter = [] } = instanceData.constants_info || {}
                    Object.keys(pipelineData.constants).forEach(key => {
                        const cnt = pipelineData.constants[key]
                        if (cnt.show_type === 'show') {
                            if (!has_key || keys_in_constants_parameter.includes(key)) {
                                // api调用时不做校验
                                cnt.validation = ''
                                constants[key] = cnt
                            }
                        }
                    })
                    this.isChildTaskFlow = instanceData.is_child_taskflow
                    this.constants = constants
                } catch (e) {
                    console.log(e)
                } finally {
                    this.cntLoading = false
                }
            },
            async getUnUsedConstants () {
                try {
                    const resp = await this.getTaskUsedConstants({
                        instance_id: this.instance_id
                    })
                    return resp.data.unused_constant_keys || []
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.constantLoading = false
                }
            },
            judgeDataEqual () {
                if (!this.paramsCanBeModify || !this.$refs.TaskParamEdit) {
                    return true
                }
                return this.$refs.TaskParamEdit.judgeDataEqual()
            },
            async onConfirmClick () {
                if (this.editable) { // 保存修改参数
                    this.onModifyParams()
                } else {
                    try {
                        // 如果任务正在执行中需要先暂停任务再修改参数
                        if (this.rootTaskState === 'RUNNING') {
                            this.pending = true
                            await this.instancePause(this.instance_id)
                            this.rootState = 'SUSPENDED'
                            this.$bkMessage({
                                message: i18n.t('任务已暂停执行'),
                                theme: 'success',
                                offsetY: 108
                            })
                        }
                        // 允许修改参数
                        this.editable = true
                        this.$parent.$parent.sideSliderTitle = i18n.t('修改入参')
                    } catch (error) {
                        console.warn(error)
                    } finally {
                        this.pending = false
                    }
                }
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
                // 如果节点重试时，参数为空则直接重试节点
                if (this.isParamsEmpty && this.retryNodeId) {
                    this.pending = true
                    this.$emit('nodeTaskRetry')
                    return
                }
                const paramEditComp = this.$refs.TaskParamEdit
                const formData = {}
                let metaConstants = {}
                let modifiedKeys = []
                let formValid = true
                if (paramEditComp) {
                    formValid = paramEditComp.validate()
                    if (!formValid) return false
                    const variables = await paramEditComp.getVariableData()
                    for (const key in variables) {
                        const { value, pre_render_mako } = variables[key]
                        // 执行状态下过滤掉预渲染类型的变量
                        if ((this.paramsCanBeModify && this.rootTaskState === 'CREATED') || pre_render_mako !== true) {
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
                    // 记录修改过的变量key值
                    modifiedKeys = paramEditComp.getChangeParams() || []
                }
                // 如果参数没有修改，则不用调用接口
                if (modifiedKeys.length === 0) {
                    if (this.retryNodeId) {
                        this.$emit('nodeTaskRetry')
                        return
                    }
                    // 节点暂停时提交修改，如果未修改则不继续报错直接继续执行任务
                    if (this.rootTaskState === 'SUSPENDED') {
                        this.$emit('packUp')
                        this.handleTaskResume(false)
                        return
                    }
                    this.$bkMessage({
                        message: i18n.t('参数未修改'),
                        theme: 'warning',
                        offsetY: 108
                    })
                    this.$emit('packUp')
                    return
                }
                // 传的变量值为修改过的，未修改的不传
                const constants = Object.keys(formData).reduce((acc, key) => {
                    if (modifiedKeys.includes(key)) {
                        acc[key] = formData[key]
                    }
                    return acc
                }, {})
                metaConstants = Object.keys(metaConstants).reduce((acc, key) => {
                    if (modifiedKeys.includes(key)) {
                        acc[key] = formData[key]
                    }
                    return acc
                }, {})
                const data = {
                    instance_id: this.instance_id,
                    constants,
                    meta_constants: Object.keys(metaConstants).length ? metaConstants : undefined,
                    modified_constant_keys: modifiedKeys.length ? modifiedKeys : undefined
                }
                try {
                    this.pending = true
                    /* 暂不进行变量是否被使用判断 */
                    // // 首先判断参数是否有被使用
                    // const unUsedConstants = await this.getUnUsedConstants()
                    // const usedConstants = modifiedKeys.filter(key => !unUsedConstants.includes(key))
                    // // 如果有变量被使用过则提示报错，不进行提交
                    // if (this.state !== 'CREATED' && usedConstants.length) {
                    //     const paramEditComp = this.$refs.TaskParamEdit
                    //     if (paramEditComp) {
                    //         paramEditComp.renderConfig.forEach(item => {
                    //             if (!item.attrs?.used_tip && !unUsedConstants.includes(item.tag_code)) {
                    //                 if (!item.attrs) {
                    //                     item.attrs = {}
                    //                 }
                    //                 if (usedConstants.includes(item.tag_code)) {
                    //                     item.attrs['html_used_tip'] = true
                    //                 } else {
                    //                     item.attrs['disabled'] = true
                    //                     if (item.attrs.children) {
                    //                         this.setAtomDisable(item.attrs.children)
                    //                     }
                    //                 }
                    //                 item.attrs['used_tip'] = i18n.t('参数已被使用，不可修改')
                    //             }
                    //         })
                    //         paramEditComp.randomKey = new Date().getTime()
                    //     }
                    //     this.$bkMessage({
                    //         message: i18n.t('保存失败，有参数已被使用不可修改'),
                    //         theme: 'error'
                    //     })
                    //     return
                    // }
                    const res = await this.instanceModifyParams(data)
                    if (res.result) {
                        // 修改完参数后重试节点
                        if (this.retryNodeId) {
                            this.$emit('nodeTaskRetry')
                            return
                        }
                        // 暂停的任务继续执行
                        if (this.rootTaskState === 'SUSPENDED') {
                            this.$emit('packUp')
                            this.handleTaskResume(true)
                            return
                        }
                        this.$bkMessage({
                            message: this.$t('参数修改成功'),
                            theme: 'success',
                            offsetY: 108
                        })
                        this.$emit('packUp')
                    }
                } catch (e) {
                    console.log(e)
                } finally {
                    this.pending = false
                }
            },
            // 任务重试
            handleTaskResume (hasModify = false) {
                let msgInstance = null
                let message = null
                const h = this.$createElement
                message = h('p', {
                    style: {
                        display: 'flex',
                        'align-items': 'center',
                        'justify-content': 'space-between',
                        width: '100%'
                    }
                }, [
                    h('span', {
                        display: 'hidden',
                        'white-space': 'nowrap',
                        'text-overflow': 'ellipsis'
                    }, hasModify
                        ? this.$t('已成功修改入参，是否继续执行任务？')
                        : this.$t('参数未修改，是否继续执行任务？')
                    ),
                    h('span', {
                        style: { color: '#3a84ff', cursor: 'pointer' },
                        on: {
                            click: async () => {
                                msgInstance && msgInstance.close()
                                const resp = await this.instanceResume(this.instance_id)
                                if (resp.result) {
                                    this.$bkMessage({
                                        message: this.$t('任务已继续执行'),
                                        theme: 'success',
                                        offsetY: 108
                                    })
                                    this.$parent.$parent.state = 'RUNNING'
                                    this.$parent.$parent.setTaskStatusTimer()
                                }
                            }
                        }
                    }, this.$t('继续执行'))
                ])
                msgInstance = this.$bkMessage({
                    message,
                    theme: 'success',
                    offsetY: 108,
                    delay: 10000
                })
                this.setMsgInstance(msgInstance)
            },
            setAtomDisable (atomList) {
                atomList.forEach(item => {
                    if (!item.attrs) {
                        item.attrs = {}
                    }
                    item.attrs['disabled'] = true
                    if (item.attrs.children) {
                        this.setAtomDisable(item.attrs.children)
                    }
                })
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
        display: flex;
        flex-direction: column;
        overflow: hidden;
        .bk-alert {
            margin: 10px 20px 0;
        }
        .edit-wrapper {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            @include scrollbar;
        }
        .action-wrapper {
            flex-shrink: 0;
            padding-left: 20px;
            height: 60px;
            line-height: 60px;
            border-top: 1px solid $commonBorderColor;
        }
    }
</style>
