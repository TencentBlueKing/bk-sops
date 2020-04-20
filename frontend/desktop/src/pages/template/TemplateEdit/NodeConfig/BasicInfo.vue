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
    <div class="basic-info">
        <!-- 普通插件 -->
        <bk-form
            v-if="!isSubflow"
            ref="pluginForm"
            :label-width="130"
            :model="formData"
            :rules="pluginRules">
            <bk-form-item :label="i18n.plugin" :required="true" property="plugin" class="choose-plugin-input">
                <bk-input :value="formData.name" readonly>
                    <template slot="append">
                        <div
                            class="group-text choose-plugin-btn"
                            @click="$emit('openSelectorPanel')">
                            {{ formData.plugin ? i18n.reselect : i18n.select }}
                        </div>
                    </template>
                </bk-input>
                <i class="common-icon-info form-item-tips"
                    v-if="formData.desc"
                    v-bk-tooltips="{
                        content: formData.desc,
                        width: '400',
                        placements: ['bottom-end'] }">
                </i>
            </bk-form-item>
            <bk-form-item :label="i18n.version" :required="true" property="version">
                <bk-select
                    v-model="formData.version"
                    :clearable="false"
                    @selected="$emit('versionChange', $event)">
                    <bk-option
                        v-for="item in versionList"
                        :key="item.version"
                        :id="item.version"
                        :name="item.version">
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item :label="i18n.nodeName" :required="true" property="nodeName">
                <bk-input v-model="formData.nodeName" @blur="updateData"></bk-input>
            </bk-form-item>
            <bk-form-item :label="i18n.nodeLabel" property="label">
                <bk-search-select
                    primary-key="code"
                    :clearable="true"
                    :data="labelList"
                    :show-condition="false"
                    :values="filterLabelTree(formData.nodeLabel)"
                    @change="onLabelChange">
                </bk-search-select>
            </bk-form-item>
            <bk-form-item :label="i18n.errorHandle" class="error-handle">
                <bk-checkbox
                    :value="formData.ignorable"
                    @change="onErrorHandlerChange($event, 'ignorable')">
                    <i class="error-handle-icon common-icon-dark-circle-i"></i>
                    {{ i18n.ignorable }}
                </bk-checkbox>
                <bk-checkbox
                    :value="formData.skippable"
                    :disabled="formData.ignorable"
                    @change="onErrorHandlerChange($event, 'skippable')">
                    <i class="error-handle-icon common-icon-dark-circle-s"></i>
                    {{ i18n.skip }}
                </bk-checkbox>
                <bk-checkbox
                    :value="formData.retryable"
                    :disabled="formData.ignorable"
                    @change="onErrorHandlerChange($event, 'retryable')">
                    <i class="error-handle-icon common-icon-dark-circle-r"></i>
                    {{ i18n.retry }}
                </bk-checkbox>
                <p
                    v-if="!formData.ignorable && !formData.skippable && !formData.retryable"
                    class="error-handle-tips">
                    {{ i18n.errorHandleTip }}
                </p>
                <div id="html-error-ingored-tootip" class="tips-item" style="white-space: normal;">
                    <p>{{ i18n.ignoreTip }}</p>
                    <p>{{ i18n.skipTip }}</p>
                    <p>{{ i18n.retryTip }}</p>
                </div>
                <i v-bk-tooltips="errorHandleTipsConfig" ref="tooltipsHtml" class="common-icon-info form-item-tips"></i>
            </bk-form-item>
            <bk-form-item :label="i18n.selectable">
                <bk-switcher
                    :value="formData.selectable"
                    theme="primary"
                    size="min"
                    @change="onSelectableChange">
                </bk-switcher>
            </bk-form-item>
        </bk-form>
        <!-- 子流程 -->
        <bk-form
            v-else
            ref="subflowForm"
            :label-width="130"
            :model="formData"
            :rules="subflowRules">
            <bk-form-item :label="i18n.tpl" :required="true" property="tpl">
                <bk-input :value="formData.name" readonly>
                    <template slot="append">
                        <div class="group-text choose-plugin-btn" @click="$emit('openSelectorPanel')">
                            {{ formData.tpl ? i18n.reselect : i18n.select }}
                        </div>
                    </template>
                </bk-input>
                <!-- 子流程版本更新 -->
                <i
                    class="common-icon-clock-inversion update-tooltip"
                    v-if="!inputLoading && subflowHasUpdate"
                    v-bk-tooltips="{
                        content: i18n.update,
                        placements: ['bottom-end'] }"
                    @click="onUpdateSubflowVersion">
                </i>
            </bk-form-item>
            <bk-form-item :label="i18n.nodeName" :required="true" property="nodeName">
                <bk-input v-model="formData.nodeName" @blur="updateData"></bk-input>
            </bk-form-item>
            <bk-form-item :label="i18n.nodeLabel" property="label">
                <bk-search-select
                    primary-key="code"
                    :clearable="true"
                    :data="labelList"
                    :show-condition="false"
                    :values="filterLabelTree(formData.nodeLabel)"
                    @change="onLabelChange">
                </bk-search-select>
            </bk-form-item>
            <bk-form-item :label="i18n.selectable">
                <bk-switcher
                    :value="formData.selectable"
                    theme="primary"
                    size="min"
                    @change="onSelectableChange">
                </bk-switcher>
            </bk-form-item>
        </bk-form>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapActions, mapMutations } from 'vuex'
    import { NAME_REG, STRING_LENGTH, INVALID_NAME_CHAR } from '@/constants/index.js'
    import { errorHandler } from '@/utils/errorHandler'

    export default {
        name: 'BasicInfo',
        props: {
            nodeConfig: Object,
            basicInfo: Object,
            versionList: Array,
            isSubflow: Boolean,
            inputLoading: Boolean
        },
        data () {
            return {
                labelList: [],
                labelLoading: false,
                formData: { ...this.basicInfo },
                pluginRules: {
                    plugin: [
                        {
                            required: true,
                            message: gettext('请选择插件'),
                            trigger: 'blur'
                        }
                    ],
                    version: [
                        {
                            required: true,
                            message: gettext('请选择插件版本'),
                            trigger: 'blur'
                        }
                    ],
                    nodeName: [
                        {
                            required: true,
                            message: gettext('节点名称不能为空'),
                            trigger: 'blur'
                        },
                        {
                            regex: NAME_REG,
                            message: gettext('节点名称不能包含') + INVALID_NAME_CHAR + gettext('非法字符'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH,
                            message: gettext('节点名称长度不能超过') + STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH + gettext('个字符'),
                            trigger: 'blur'
                        }
                    ]
                },
                subflowRules: {
                    tpl: [
                        {
                            required: true,
                            message: gettext('请选择流程模板'),
                            trigger: 'blur'
                        }
                    ],
                    nodeName: [
                        {
                            required: true,
                            message: gettext('节点名称不能为空'),
                            trigger: 'blur'
                        },
                        {
                            regex: NAME_REG,
                            message: gettext('节点名称不能包含') + INVALID_NAME_CHAR + gettext('非法字符'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH,
                            message: gettext('节点名称长度不能超过') + STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH + gettext('个字符'),
                            trigger: 'blur'
                        }
                    ]
                },
                errorHandleTipsConfig: {
                    allowHtml: true,
                    width: 400,
                    content: '#html-error-ingored-tootip',
                    placement: 'bottom-end'
                },
                i18n: {
                    select: gettext('选择'),
                    reselect: gettext('重选'),
                    plugin: gettext('标准插件'),
                    version: gettext('插件版本'),
                    update: gettext('版本更新'),
                    nodeName: gettext('节点名称'),
                    nodeLabel: gettext('节点标签'),
                    step: gettext('步骤名称'),
                    errorHandle: gettext('失败处理'),
                    selectable: gettext('是否可选'),
                    ignorable: gettext('自动忽略'),
                    skip: gettext('手动跳过'),
                    retry: gettext('手动重试'),
                    tpl: gettext('流程模板'),
                    errorHandleTip: gettext('未选择失败处理方式，标准插件节点如果执行失败，会导致任务中断后不可继续'),
                    explanation: gettext('说明：'),
                    ignoreTip: gettext('自动忽略：标准插件节点如果执行失败，会自动忽略错误并把节点状态设置为成功。'),
                    skipTip: gettext('手动跳过：标准插件节点如果执行失败，可以人工干预，直接跳过节点的执行。'),
                    retryTip: gettext('手动重试：标准插件节点如果执行失败，可以人工干预，填写参数后重试节点。')
                }
            }
        },
        computed: {
            ...mapState({
                'subprocessInfo': state => state.template.subprocess_info
            }),
            subflowHasUpdate () {
                return this.subprocessInfo.details.some(subflow => {
                    if (
                        subflow.expired
                        && subflow.template_id === Number(this.formData.tpl)
                        && subflow.subprocess_node_id === this.nodeConfig.id
                    ) {
                        return true
                    }
                })
            }
        },
        watch: {
            basicInfo (val) {
                this.formData = { ...val }
            }
        },
        created () {
            this.getNodeLabelList()
        },
        methods: {
            ...mapMutations('template/', [
                'setNodeBasicInfo'
            ]),
            ...mapActions('template/', [
                'getLabels'
            ]),
            // 加载节点标签列表
            async getNodeLabelList () {
                try {
                    this.labelLoading = true
                    const resp = await this.getLabels({ limit: 0 })
                    this.labelList = this.transLabelListToGroup(resp.objects)
                } catch (error) {
                    errorHandler(error, this)
                } finally {
                    this.labelLoading = false
                }
            },
            // 标签分组
            transLabelListToGroup (list) {
                const data = []
                const groups = []
                list.forEach(item => {
                    const index = groups.findIndex(code => code === item.group.code)
                    if (index > -1) {
                        data[index].children.push(item)
                    } else {
                        const { code, name } = item.group
                        data.push({
                            code,
                            name,
                            children: [{ ...item }]
                        })
                        groups.push(item.group.code)
                    }
                })
                return data
            },
            /**
             * 由节点保存的标签数据格式，转换成 searchSelect 组件要求的 values 格式
             */
            filterLabelTree (val) {
                // 等待节点标签列表加载完成，再做筛选
                if (this.labelLoading) {
                    return []
                }

                const data = []
                val.forEach(item => {
                    const group = this.labelList.find(g => g.code === item.group)
                    const label = group.children.find(l => l.code === item.label)
                    data.push({
                        code: group.code,
                        name: group.name,
                        values: [
                            {
                                code: label.code,
                                name: label.name
                            }
                        ]
                    })
                })
                return data
            },
            onLabelChange (list) {
                const val = []
                list.forEach(item => {
                    val.push({
                        label: item.values[0].code,
                        group: item.code
                    })
                })
                this.formData.nodeLabel = val
                this.updateData()
            },
            onErrorHandlerChange (val, type) {
                this.formData[type] = val
                if (type === 'ignorable' && val) {
                    this.formData.retryable = false
                    this.formData.skippable = false
                }
                this.updateData()
            },
            onSelectableChange (val) {
                this.formData.selectable = val
                this.updateData()
            },
            updateData () {
                const { version, nodeName, nodeLabel, ignorable, skippable, retryable, selectable } = this.formData
                let data
                if (this.isSubflow) {
                    data = { nodeName, nodeLabel, selectable }
                } else {
                    data = { version, nodeName, nodeLabel, ignorable, skippable, retryable, selectable }
                }
                this.$emit('update', data)
            },
            /**
             * 子流程版本更新
             */
            onUpdateSubflowVersion () {
                if (this.inputLoading) {
                    return
                }

                this.$emit('updateSubflowVersion')
            },
            validate () {
                const comp = this.isSubflow ? this.$refs.subflowForm : this.$refs.pluginForm
                comp.clearError()
                return comp.validate()
            }
        }
    }
</script>
<style lang="scss" scoped>
    .basic-info {
        padding-right: 30px;
    }
    .error-handle {
        /deep/ .bk-form-checkbox {
            margin-right: 30px;
            &.is-disabled .bk-checkbox-text {
                color: #c4c6cc;
            }
        }
        .error-handle-icon {
            padding-right: 4px;
            color: #a6b0c7;
        }
        .error-handle-tips {
            font-size: 12px;
            line-height: 1;
            color: #ffb400;
        }
    }
    /deep/ .bk-form {
        .bk-label {
            font-size: 12px;
        }
        .bk-checkbox-text {
            font-size: 12px;
            color: #63656e;
        }
        .bk-form-control .group-box.group-append {
            margin-left: -1px;
            z-index: 11;
            border: 1px solid #3a84ff;
        }
        .form-item-tips {
            position: absolute;
            right: -30px;
            top: 7px;
            color: #c4c6cc;
            &:hover {
                color: #f4aa1a;
            }
        }
        .choose-plugin-btn {
            width: 68px;
            height: 30px;
            line-height: 30px;
            color: #3a84ff;
            background: #e1ecff;
            text-align: center;
            cursor: pointer;
        }
        .choose-plugin-input {
            .bk-form-input[readonly] {
                border-color: #c4c6cc !important;
            }
        }
        .update-tooltip {
            position: absolute;
            right: -28px;
            top: 8px;
            cursor: pointer;
            color: #3a84ff;
        }
    }
    .bk-option-content {
        &:hover {
            .open-link-icon {
                display: inline-block;
            }
        }
        .open-link-icon {
            display: none;
            float: right;
            margin-top: 10px;
        }
    }
</style>
