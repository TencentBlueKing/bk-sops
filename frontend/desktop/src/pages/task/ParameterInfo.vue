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
    <div :class="['parameter-info-wrap', { 'no-data': isNoData }]" v-bkloading="{ isLoading: isParameterInfoLoading, opacity: 1, zIndex: 100 }">
        <TaskParamEdit
            v-if="isReferencedShow"
            class="task-param-wrapper"
            ref="taskParamEdit"
            :constants="refVariable"
            @blur="setRenderFormConfig"
            @change="handleFormChange"
            @onChangeConfigLoading="onRefVarLoadingChange">
        </TaskParamEdit>
        <div
            class="variable-wrap"
            v-if="isUnreferencedShow">
            <div class="title-background" @click="onToggleUnreferenceShow">
                <div :class="['unreferenced-variable', { 'unreference-show': isUnrefVarShow }]"></div>
                <span class="title">{{$t('查看未引用变量')}}</span>
                <i class="common-icon-info desc-tooltip"
                    v-bk-tooltips="{
                        content: $t('在编辑流程模板时，可以通过变量引擎支持的语法引用全局变量，未引用的变量不可编辑'),
                        width: '400',
                        placements: ['bottom-end'] }">
                </i>
            </div>
            <TaskParamEdit
                class="unreferenced"
                ref="unRefTaskParamEdit"
                v-show="isUnrefVarShow"
                :show-required="false"
                :constants="unRefVariable"
                :editable="false"
                @onChangeConfigLoading="onUnrefVarLoadingChange">
            </TaskParamEdit>
        </div>
        <NoData v-if="isNoData" :message="$t('暂无参数')"></NoData>
    </div>
</template>
<script>
    import tools from '@/utils/tools.js'
    import { mapState, mapActions, mapGetters } from 'vuex'
    import TaskParamEdit from './TaskParamEdit.vue'
    import NoData from '@/components/common/base/NoData.vue'
    export default {
        name: 'ParameterInfo',
        components: {
            TaskParamEdit,
            NoData
        },
        props: [
            'common',
            'projectId',
            'referencedVariable',
            'unReferencedVariable',
            'taskMessageLoading'
        ],
        data () {
            return {
                isUnrefVarShow: false,
                isRefVarLoading: true,
                isUnrefVarLoading: true,
                renderConfig: [],
                renderData: {},
                refVariable: {},
                unRefVariable: {},
                variableCited: {},
                watchVarInfo: {},
                changeVarInfo: {},
                isVariableLoading: true,
                wasChangeVarMap: {
                    wasRef: [],
                    wasUnRef: []
                }
            }
        },
        computed: {
            ...mapState({
                'username': state => state.username,
                'bizId': state => state.project.bizId,
                'activities': state => state.template.activities,
                'gateways': state => state.template.gateways,
                'constants': state => state.template.constants,
                'internalVariable': state => state.template.internalVariable
            }),
            isReferencedShow () {
                return this.getReferencedStatus(this.refVariable)
            },
            isUnreferencedShow () {
                if (this.taskMessageLoading) return false
                const variableKeys = Object.keys(this.unRefVariable)
                const unreferenced = variableKeys.filter(key => this.unRefVariable[key].show_type === 'show')
                return !!unreferenced.length
            },
            isParameterInfoLoading () {
                return this.isRefVarLoading || this.isUnrefVarLoading || this.isVariableLoading
            },
            isNoData () {
                return !this.taskMessageLoading && !this.isReferencedShow && !this.isUnreferencedShow && !this.isVariableLoading
            }
        },
        watch: {
            isParameterInfoLoading (val) {
                this.$emit('paramsLoadingChange', val)
                if (!val && Object.keys(this.watchVarInfo).length) {
                    this.getRenderConfig()
                    for (const [key, value] of Object.entries(this.renderData)) {
                        const result = this.setVariableHideLogic(key, value)
                        if (result) {
                            this.updateRenderFormConfig()
                        }
                    }
                }
            },
            taskMessageLoading (val) {
                if (!val) {
                    if (!this.isReferencedShow) {
                        this.isRefVarLoading = false
                    }
                    if (!this.isUnreferencedShow) {
                        this.isUnrefVarLoading = false
                    }
                    // 获取变量引用关系
                    this.getVariableCitedData()
                    // 获取监听变量字典
                    this.getVarChangeMap()
                    // 更新变量
                    this.updateReferencedConstants()
                }
            }
        },
        mounted () {
            this.setRenderFormConfig = tools.debounce(this.handleFormBlur, 500)
        },
        methods: {
            ...mapActions('template/', [
                'getTaskReferencedConstants',
                'getVariableCite'
            ]),
            ...mapGetters('template/', [
                'getPipelineTree'
            ]),
            onToggleUnreferenceShow () {
                this.isUnrefVarShow = !this.isUnrefVarShow
            },
            onRefVarLoadingChange (val) {
                this.isRefVarLoading = val
            },
            onUnrefVarLoadingChange (val) {
                this.isUnrefVarLoading = val
            },
            // 获取 TaskParamEdit
            getTaskParamEdit () {
                return this.$refs.taskParamEdit
            },
            getReferencedStatus (variable) {
                return (this.taskMessageLoading || !variable)
                    ? false
                    : !!Object.keys(variable).length
            },
            async handleFormChange (formData, key) {
                // 获取所有变量的配置,数据
                if (!this.renderConfig.length) {
                    this.getRenderConfig()
                } else {
                    // 更新renderData
                    Object.assign(this.renderData, formData)
                }
                // 如果类型为输入框/下拉框/文本框/数字框，则不进行后续处理
                const config = this.renderConfig.find(item => item.tag_code === key)
                if (!config || ['input', 'select', 'textarea', 'int'].includes(config.type)) return

                this.handleFormBlur(key)
            },
            // 表单项失焦
            async handleFormBlur (key) {
                let result = false
                // "显示参数"条件隐藏
                if (Object.keys(this.watchVarInfo).length) {
                    this.wasChangeVarMap = {
                        wasRef: [],
                        wasUnRef: []
                    }
                    const value = this.renderData[key]
                    result = this.setVariableHideLogic(key, value)
                }
                // 该变量被网关分支引用时，更新参数引用
                if (this.variableCited[key]?.conditions.length) {
                    await this.updateReferencedConstants()
                    result = true
                }
                if (result) {
                    this.updateRenderFormConfig()
                }
            },
            // 获取引用区和未引用区的变量配置
            getRenderConfig () {
                const taskParamEdit = this.$refs.taskParamEdit
                const unRefTaskParamEdit = this.$refs.unRefTaskParamEdit
                this.renderConfig = [
                    ...taskParamEdit?.renderConfig || [],
                    ...unRefTaskParamEdit?.renderConfig || []
                ] || []
                this.renderData = {
                    ...taskParamEdit?.renderData || {},
                    ...unRefTaskParamEdit?.renderData || {}
                } || {}
            },
            // 更新参数引用
            async updateReferencedConstants () {
                try {
                    const constants = Object.values(this.constants).reduce((acc, cur) => {
                        const value = cur.key in this.renderData ? this.renderData[cur.key] : cur.value
                        acc[cur.key] = {
                            ...cur,
                            value
                        }
                        return acc
                    }, {})
                    const pipelineTree = this.getPipelineTree()
                    const data = {
                        constants,
                        extra_data: {
                            executor: this.username,
                            project_id: this.common ? undefined : this.projectId,
                            biz_cc_id: this.common ? undefined : this.bizId
                        },
                        pipeline_tree: JSON.stringify(pipelineTree)
                    }
                    const resp = await this.getTaskReferencedConstants(data)
                    if (!resp.result) return
                    const referenced = resp.data.referenced_constants
                    const refVariable = {}
                    const unRefVariable = {}
                    // 重新计算引用区和未引用区的变量
                    const { wasRef, wasUnRef } = this.wasChangeVarMap
                    for (const [key, value] of Object.entries(this.constants)) {
                        if (wasRef.includes(key)) {
                            refVariable[key] = value
                        } else if (wasUnRef.includes(key)) {
                            unRefVariable[key] = value
                        } else if (referenced.includes(key)) {
                            refVariable[key] = value
                        } else {
                            unRefVariable[key] = value
                        }
                    }
                    this.refVariable = refVariable
                    this.unRefVariable = unRefVariable
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isVariableLoading = false
                }
            },
            // 获取节点与变量的依赖关系
            async getVariableCitedData () {
                try {
                    const constants = { ...this.internalVariable, ...this.constants }
                    const data = {
                        activities: this.activities,
                        gateways: this.gateways,
                        constants
                    }
                    const resp = await this.getVariableCite(data)
                    if (resp.result) {
                        this.variableCited = resp.data.defined
                    }
                } catch (e) {
                    console.log(e)
                }
            },
            getVarChangeMap () {
                // 设置变量自动隐藏对象
                const watchVarInfo = {}
                const changeVarInfo = {}
                const constants = { ...this.internalVariable, ...this.constants }
                Object.values(constants).forEach(item => {
                    if (!item.hide_condition || !item.hide_condition.length) return
                    item.hide_condition.forEach(val => {
                        const { constant_key: key, operator, value } = val
                        // 隐藏的变量和对应的监听变量
                        if (!(item.key in changeVarInfo)) {
                            changeVarInfo[item.key] = {}
                        }
                        changeVarInfo[item.key][key] = false
                        // 监听的变量和对应的隐藏变量
                        const params = {
                            target_key: item.key,
                            operator,
                            value,
                            isOr: true // 与逻辑或或逻辑 默认或逻辑
                        }
                        if (key in watchVarInfo) {
                            watchVarInfo[key].push(params)
                        } else {
                            watchVarInfo[key] = [params]
                        }
                    })
                })
                this.watchVarInfo = watchVarInfo
                this.changeVarInfo = changeVarInfo
            },
            // 设置变量隐藏逻辑
            setVariableHideLogic (key, val) {
                if (!(key in this.watchVarInfo)) return false
                let result = true
                const values = this.watchVarInfo[key]
                values.forEach(item => {
                    let isEqual = JSON.stringify(val) === JSON.stringify(item.value)
                    const relatedVarInfo = this.changeVarInfo[item.target_key]
                    // 计算输入值是否匹配
                    isEqual = (item.operator === '=' && isEqual) || (item.operator === '!=' && !isEqual)
                    relatedVarInfo[key] = isEqual
                    // 相关运算逻辑
                    let isMatch = false
                    const relatedVarValues = Object.values(relatedVarInfo)
                    if (item.isOr) {
                        isMatch = relatedVarValues.some(option => option)
                    } else {
                        isMatch = relatedVarValues.every(option => option)
                    }
                    if (isMatch) {
                        // 匹配成功时将对应的变量从引用区挪到未引用区
                        const varInfo = tools.deepClone(this.refVariable[item.target_key])
                        this.$delete(this.refVariable, item.target_key)
                        this.unRefVariable[item.target_key] = varInfo
                        // 将被改变显示/隐藏的变量记录起来
                        this.wasChangeVarMap.wasUnRef.push(item.target_key)
                    } else if (!this.refVariable[item.target_key]) {
                        // 匹配失败后，如果引用区没有对应的变量需要从未引用区挪出来
                        const varInfo = tools.deepClone(this.unRefVariable[item.target_key])
                        this.$delete(this.unRefVariable, item.target_key)
                        this.refVariable[item.target_key] = varInfo
                        this.wasChangeVarMap.wasRef.push(item.target_key)
                    } else {
                        result = false
                    }
                })
                return result
            },
            updateRenderFormConfig () {
                const taskParamEdit = this.$refs.taskParamEdit
                const unRefTaskParamEdit = this.$refs.unRefTaskParamEdit
                // 更新引用去/未引用区变量的配置，表单值
                const paramEditRefs = [taskParamEdit, unRefTaskParamEdit]
                paramEditRefs.forEach((paramEditRef, index) => {
                    if (!taskParamEdit) return
                    const variable = index ? this.unRefVariable : this.refVariable
                    paramEditRef.formScheme = this.renderConfig.filter(item => item.tag_code in variable)
                    paramEditRef.renderData = paramEditRef.formScheme.reduce((acc, cur) => {
                        acc[cur.tag_code] = this.renderData[cur.tag_code]
                        return acc
                    }, {})
                    paramEditRef.randomKey = new Date().getTime()
                })
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.task-param-wrapper {
    max-width: 100%;
    margin: 0 20px 20px 20px;
}
.parameter-info-wrap {
    min-height: 200px;
}
.variable-wrap {
    background: #f0f1f5;
    .unreferenced {
       padding-bottom: 20px;
    }
    .title-background {
        position: relative;
        padding-left: 20px;
        cursor: pointer;
        &:hover {
            background: #e4e6ed;
        }
        .unreferenced-variable {
            display: inline-block;
            position: relative;
            width: 0;
            height: 0;
            border-left: 5px solid gray;
            border-top: 5px solid transparent;
            border-right: 5px solid transparent;
            border-bottom: 5px solid transparent;
        }
        .unreference-show {
            top: 2px;
            transform: rotate(90deg);
        }
        .desc-tooltip {
            position: absolute;
            right: 20px;
            top: 22px;
            color: #c4c6cc;
            &:hover {
                color: #f4aa1a;
            }
        }
        .title {
            font-weight: 600;
            line-height: 60px;
            font-size: 14px
        }
    }
}
/deep/ .render-form {
    .el-input__inner,
    .el-tree,
    .el-date-editor,
    .el-textarea__inner,
    .el-input-number,
    .tag-input,
    .el-date-editor,
    .el-cascader,
    .el-select,
    .user-selector-layout,
    /deep/ .ip-search-wrap {
        max-width: 598px;
    }
    /deep/.module-form  {
        .bk-form-content,
        .bk-input-number,
        .bk-select {
            max-width: 598px;
        }
    }
    .el-radio__label,
    .checkbox-item {
        max-width: 160px;
        margin-right: 24px;
    }
}
.no-data {
    /deep/ .no-data-wrapper {
        position: relative;
        top: 90px;
    }
}
</style>
