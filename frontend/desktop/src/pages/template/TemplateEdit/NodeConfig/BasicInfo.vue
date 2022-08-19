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
    <div class="basic-info">
        <!-- 普通插件 -->
        <bk-form
            v-if="!isSubflow"
            ref="pluginForm"
            :label-width="130"
            :model="formData"
            :rules="pluginRules">
            <bk-form-item :label="$t('标准插件')" :required="true" property="plugin" class="choose-plugin-input">
                <bk-input :value="formData.name" readonly>
                    <template slot="append">
                        <div
                            :class="['operate-btn', { 'is-disabled': isViewMode }]"
                            @click="openSelectorPanel">
                            {{ formData.plugin ? $t('重选') : $t('选择') }}
                        </div>
                    </template>
                </bk-input>
                <p v-if="formData.desc" class="plugin-info-desc" v-html="formData.desc"></p>
            </bk-form-item>
            <bk-form-item :label="$t('插件版本')" data-test-id="templateEdit_form_pluginVersion" :required="true" property="version">
                <bk-select
                    v-model="formData.version"
                    :clearable="false"
                    :disabled="isViewMode"
                    @selected="$emit('versionChange', $event)">
                    <bk-option
                        v-for="item in versionList"
                        :key="item.version"
                        :id="item.version"
                        :name="item.version">
                    </bk-option>
                </bk-select>
            </bk-form-item>
            <bk-form-item :label="$t('节点名称')" data-test-id="templateEdit_form_nodeName" :required="true" property="nodeName">
                <bk-input :readonly="isViewMode" v-model="formData.nodeName" @change="updateData"></bk-input>
            </bk-form-item>
            <bk-form-item :label="$t('步骤名称')" data-test-id="templateEdit_form_stageName" property="stageName">
                <bk-input :readonly="isViewMode" v-model="formData.stageName" @change="updateData"></bk-input>
            </bk-form-item>
            <!-- <bk-form-item :label="$t('节点标签')" data-test-id="templateEdit_form_nodeLabel" property="label">
                <bk-search-select
                    primary-key="code"
                    :ext-cls="isViewMode ? 'disabled-search' : ''"
                    :clearable="true"
                    :popover-zindex="2300"
                    :data="labelList"
                    :show-condition="false"
                    :show-popover-tag-change="false"
                    :values="filterLabelTree(formData.nodeLabel)"
                    @change="onLabelChange"
                    @clear="onLabelClear">
                </bk-search-select>
            </bk-form-item> -->
            <bk-form-item :label="$t('失败处理')">
                <div class="error-handle">
                    <bk-checkbox
                        :value="formData.ignorable"
                        :disabled="isViewMode || formData.autoRetry.enable || formData.timeoutConfig.enable"
                        @change="onErrorHandlerChange($event, 'ignorable')">
                        <span class="error-handle-icon"><span class="text">AS</span></span>
                        {{ $t('自动跳过') }}
                    </bk-checkbox>
                    <bk-checkbox
                        :value="formData.skippable"
                        :disabled="isViewMode || formData.ignorable"
                        @change="onErrorHandlerChange($event, 'skippable')">
                        <span class="error-handle-icon"><span class="text">MS</span></span>
                        {{ $t('手动跳过') }}
                    </bk-checkbox>
                    <bk-checkbox
                        :value="formData.retryable"
                        :disabled="isViewMode || formData.ignorable || formData.autoRetry.enable"
                        @change="onErrorHandlerChange($event, 'retryable')">
                        <span class="error-handle-icon"><span class="text">MR</span></span>
                        {{ $t('手动重试') }}
                    </bk-checkbox>
                    <bk-checkbox
                        :value="formData.autoRetry.enable"
                        :disabled="isViewMode || formData.ignorable || formData.timeoutConfig.enable"
                        @change="onErrorHandlerChange($event, 'autoRetry')">
                        <span class="error-handle-icon"><span class="text">AR</span></span>
                    </bk-checkbox>
                    <span class="auto-retry-times">
                        {{ $t('在') }}
                        <div class="number-input" style="margin: 0 4px;">
                            <bk-input
                                v-model.number="formData.autoRetry.interval"
                                type="number"
                                style="width: 68px;"
                                :placeholder="' '"
                                :disabled="isViewMode || !formData.autoRetry.enable"
                                :max="10"
                                :min="0"
                                :precision="0"
                                @change="updateData">
                            </bk-input>
                            <span class="unit">{{ $tc('秒', 0) }}</span>
                        </div>
                        {{ $t('后') }}{{ $t('，') }}{{ $t('自动重试') }}
                        <div class="number-input" style=" margin-left: 4px;">
                            <bk-input
                                v-model.number="formData.autoRetry.times"
                                type="number"
                                style="width: 68px;"
                                :placeholder="' '"
                                :disabled="isViewMode || !formData.autoRetry.enable"
                                :max="10"
                                :min="1"
                                :precision="0"
                                @change="updateData">
                            </bk-input>
                            <span class="unit">{{ $t('次') }}</span>
                        </div>
                    </span>
                </div>
                <p
                    v-if="!formData.ignorable && !formData.skippable && !formData.retryable && !formData.autoRetry.enable"
                    class="error-handle-tips">
                    {{ $t('未选择失败处理方式，标准插件节点如果执行失败，会导致任务中断后不可继续') }}
                </p>
                <div id="html-error-ingored-tootip" class="tips-item" style="white-space: normal;">
                    <p>{{ $t('自动忽略：标准插件节点如果执行失败，会自动忽略错误并把节点状态设置为成功。') }}</p>
                    <p>{{ $t('手动跳过：标准插件节点如果执行失败，可以人工干预，直接跳过节点的执行。') }}</p>
                    <p>{{ $t('手动重试：标准插件节点如果执行失败，可以人工干预，填写参数后重试节点。') }}</p>
                    <p>{{ $t('自动重试：标准插件节点如果执行失败，系统会自动以原参数进行重试。') }}</p>
                </div>
                <i v-bk-tooltips="errorHandleTipsConfig" ref="tooltipsHtml" class="bk-icon icon-question-circle form-item-tips"></i>
            </bk-form-item>
            <bk-form-item :label="$t('超时控制')">
                <div class="timeout-setting-wrap">
                    <bk-switcher
                        theme="primary"
                        size="small"
                        style="margin-right: 8px;"
                        :value="formData.timeoutConfig.enable"
                        :disabled="isViewMode || formData.ignorable || formData.autoRetry.enable"
                        @change="onTimeoutChange">
                    </bk-switcher>
                    <template v-if="formData.timeoutConfig.enable">
                        {{ $t('超时') }}
                        <div class="number-input" style="margin: 0 4px;">
                            <bk-input
                                v-model.number="formData.timeoutConfig.seconds"
                                type="number"
                                style="width: 75px;"
                                :placeholder="' '"
                                :min="10"
                                :max="maxNodeExecuteTimeout"
                                :precision="0"
                                :readonly="isViewMode"
                                @change="updateData">
                            </bk-input>
                            <span class="unit">{{ $tc('秒', 0) }}</span>
                        </div>
                        {{ $t('后') }}{{ $t('，') }}{{ $t('则') }}
                        <bk-select
                            style="width: 160px; margin-left: 4px;"
                            v-model="formData.timeoutConfig.action"
                            :disabled="isViewMode"
                            :clearable="false" @change="updateData">
                            <bk-option id="forced_fail" :name="$t('强制失败')"></bk-option>
                            <bk-option id="forced_fail_and_skip" :name="$t('强制失败后跳过')"></bk-option>
                        </bk-select>
                    </template>
                </div>
                <p v-if="formData.timeoutConfig.enable" class="error-handle-tips" style="margin-top: 6px;">
                    {{ $t('该功能仅对V2引擎生效') }}
                </p>
            </bk-form-item>
            <bk-form-item :label="$t('是否可选')">
                <bk-switcher
                    theme="primary"
                    size="small"
                    :value="formData.selectable"
                    :disabled="isViewMode"
                    @change="onSelectableChange">
                </bk-switcher>
            </bk-form-item>
            <bk-form-item v-if="common" :label="$t('执行代理人')" data-test-id="templateEdit_form_executor_proxy">
                <bk-user-selector
                    :disabled="isViewMode"
                    v-model="formData.executor_proxy"
                    :placeholder="$t('请输入用户')"
                    :api="userApi"
                    :multiple="false"
                    @change="onUserSelectChange">
                </bk-user-selector>
            </bk-form-item>
        </bk-form>
        <!-- 子流程 -->
        <bk-form
            v-else
            ref="subflowForm"
            :label-width="130"
            :model="formData"
            :rules="subflowRules">
            <bk-form-item :label="$t('流程模板')" :required="true" property="tpl">
                <bk-input :value="formData.name" readonly>
                    <template slot="append">
                        <div
                            v-if="basicInfo.tpl"
                            class="view-subflow"
                            @click="$emit('viewSubflow', basicInfo.tpl)">
                            <i class="bk-icon common-icon-box-top-right-corner"></i>
                        </div>
                        <div :class="['operate-btn', { 'is-disabled': isViewMode }]" @click="openSelectorPanel">
                            {{ formData.tpl ? $t('重选') : $t('选择') }}
                        </div>
                    </template>
                </bk-input>
                <!-- 子流程版本更新 -->
                <p class="update-tooltip" v-if="!inputLoading && subflowHasUpdate && !subflowUpdated">
                    {{ $t('子流程有更新，更新时若存在相同表单数据则获取原表单的值。') }}
                    <bk-button :text="true" title="primary" :disabled="isViewMode" @click="onUpdateSubflowVersion">{{ $t('更新子流程') }}</bk-button>
                </p>
            </bk-form-item>
            <bk-form-item :label="$t('节点名称')" :required="true" property="nodeName">
                <bk-input :readonly="isViewMode" v-model="formData.nodeName" @change="updateData"></bk-input>
            </bk-form-item>
            <bk-form-item :label="$t('步骤名称')" property="stageName">
                <bk-input :readonly="isViewMode" v-model="formData.stageName" @change="updateData"></bk-input>
            </bk-form-item>
            <bk-form-item :label="$t('执行方案')">
                <bk-select
                    :value="formData.schemeIdList"
                    :clearable="false"
                    :multiple="true"
                    :loading="schemeListLoading"
                    :disabled="isViewMode"
                    @selected="onSelectTaskScheme">
                    <bk-option v-for="item in schemeList" :key="item.id" :id="item.id" :name="item.name"></bk-option>
                </bk-select>
                <i
                    v-bk-tooltips="{
                        width: 300,
                        placement: 'bottom-end',
                        content: $t('每次创建任务会使用选中执行方案的最新版本且不会提示该节点需要更新')
                    }"
                    class="bk-icon icon-question-circle form-item-tips">
                </i>
            </bk-form-item>
            <template v-if="formEnable">
                <bk-form-item :label="$t('失败处理')">
                    <div class="error-handle">
                        <bk-checkbox
                            :value="formData.ignorable"
                            :disabled="isViewMode || formData.autoRetry.enable || formData.timeoutConfig.enable"
                            @change="onErrorHandlerChange($event, 'ignorable')">
                            <span class="error-handle-icon"><span class="text">AS</span></span>
                            {{ $t('自动跳过') }}
                        </bk-checkbox>
                        <bk-checkbox
                            :value="formData.skippable"
                            :disabled="isViewMode || formData.ignorable"
                            @change="onErrorHandlerChange($event, 'skippable')">
                            <span class="error-handle-icon"><span class="text">MS</span></span>
                            {{ $t('手动跳过') }}
                        </bk-checkbox>
                        <bk-checkbox
                            :value="formData.retryable"
                            :disabled="isViewMode || formData.ignorable || formData.autoRetry.enable"
                            @change="onErrorHandlerChange($event, 'retryable')">
                            <span class="error-handle-icon"><span class="text">MR</span></span>
                            {{ $t('手动重试') }}
                        </bk-checkbox>
                        <bk-checkbox
                            :value="formData.autoRetry.enable"
                            :disabled="isViewMode || formData.ignorable || formData.timeoutConfig.enable"
                            @change="onErrorHandlerChange($event, 'autoRetry')">
                            <span class="error-handle-icon"><span class="text">AR</span></span>
                        </bk-checkbox>
                        <span class="auto-retry-times">
                            {{ $t('在') }}
                            <div class="number-input" style="margin: 0 4px;">
                                <bk-input
                                    v-model.number="formData.autoRetry.interval"
                                    type="number"
                                    style="width: 68px;"
                                    :placeholder="' '"
                                    :disabled="isViewMode || !formData.autoRetry.enable"
                                    :max="10"
                                    :min="0"
                                    :precision="0"
                                    @change="updateData">
                                </bk-input>
                                <span class="unit">{{ $tc('秒', 0) }}</span>
                            </div>
                            {{ $t('后') }}{{ $t('，') }}{{ $t('自动重试') }}
                            <div class="number-input" style=" margin-left: 4px;">
                                <bk-input
                                    v-model.number="formData.autoRetry.times"
                                    type="number"
                                    style="width: 68px;"
                                    :placeholder="' '"
                                    :disabled="isViewMode || !formData.autoRetry.enable"
                                    :max="10"
                                    :min="1"
                                    :precision="0"
                                    @change="updateData">
                                </bk-input>
                                <span class="unit">{{ $t('次') }}</span>
                            </div>
                        </span>
                    </div>
                    <p
                        v-if="!formData.ignorable && !formData.skippable && !formData.retryable && !formData.autoRetry.enable"
                        class="error-handle-tips">
                        {{ $t('未选择失败处理方式，标准插件节点如果执行失败，会导致任务中断后不可继续') }}
                    </p>
                    <div id="html-error-ingored-tootip" class="tips-item" style="white-space: normal;">
                        <p>{{ $t('自动忽略：标准插件节点如果执行失败，会自动忽略错误并把节点状态设置为成功。') }}</p>
                        <p>{{ $t('手动跳过：标准插件节点如果执行失败，可以人工干预，直接跳过节点的执行。') }}</p>
                        <p>{{ $t('手动重试：标准插件节点如果执行失败，可以人工干预，填写参数后重试节点。') }}</p>
                        <p>{{ $t('自动重试：标准插件节点如果执行失败，系统会自动以原参数进行重试。') }}</p>
                    </div>
                    <i v-bk-tooltips="errorHandleTipsConfig" ref="tooltipsHtml" class="bk-icon icon-question-circle form-item-tips"></i>
                </bk-form-item>
                <bk-form-item :label="$t('超时控制')">
                    <div class="timeout-setting-wrap">
                        <bk-switcher
                            theme="primary"
                            size="small"
                            style="margin-right: 8px;"
                            :value="formData.timeoutConfig.enable"
                            :disabled="isViewMode || formData.ignorable || formData.autoRetry.enable"
                            @change="onTimeoutChange">
                        </bk-switcher>
                        <template v-if="formData.timeoutConfig.enable">
                            {{ $t('超时') }}
                            <div class="number-input" style="margin: 0 4px;">
                                <bk-input
                                    v-model.number="formData.timeoutConfig.seconds"
                                    type="number"
                                    style="width: 75px;"
                                    :placeholder="' '"
                                    :min="10"
                                    :max="maxNodeExecuteTimeout"
                                    :precision="0"
                                    :readonly="isViewMode"
                                    @change="updateData">
                                </bk-input>
                                <span class="unit">{{ $tc('秒', 0) }}</span>
                            </div>
                            {{ $t('后') }}{{ $t('，') }}{{ $t('则') }}
                            <bk-select
                                style="width: 160px; margin-left: 4px;"
                                v-model="formData.timeoutConfig.action"
                                :disabled="isViewMode"
                                :clearable="false" @change="updateData">
                                <bk-option id="forced_fail" :name="$t('强制失败')"></bk-option>
                                <bk-option id="forced_fail_and_skip" :name="$t('强制失败后跳过')"></bk-option>
                            </bk-select>
                        </template>
                    </div>
                    <p v-if="formData.timeoutConfig.enable" class="error-handle-tips" style="margin-top: 6px;">
                        {{ $t('该功能仅对V2引擎生效') }}
                    </p>
                </bk-form-item>
            </template>
            <bk-form-item :label="$t('是否可选')">
                <bk-switcher
                    theme="primary"
                    size="small"
                    :disabled="isViewMode"
                    :value="formData.selectable"
                    @change="onSelectableChange">
                </bk-switcher>
            </bk-form-item>
            <bk-form-item :label="$t('总是使用最新版本')">
                <bk-switcher
                    theme="primary"
                    size="small"
                    :disabled="isViewMode"
                    :value="formData.alwaysUseLatest"
                    @change="onAlwaysUseLatestChange">
                </bk-switcher>
                <i
                    v-bk-tooltips="{
                        width: 540,
                        placement: 'bottom-end',
                        content: $t('打开该开关后，每次创建任务会尝试使用子流程的最新版本，并且不会再提示该节点需要更新，如果子流程中增加了新的变量，在不更新子流程版本的情况下，会使用变量默认值')
                    }"
                    class="bk-icon icon-question-circle form-item-tips">
                </i>
            </bk-form-item>
            <bk-form-item v-if="common" :label="$t('执行代理人')" data-test-id="templateEdit_form_executor_proxy">
                <bk-user-selector
                    :disabled="isViewMode"
                    v-model="formData.executor_proxy"
                    :placeholder="$t('请输入用户')"
                    :api="userApi"
                    :multiple="false"
                    @change="onUserSelectChange">
                </bk-user-selector>
            </bk-form-item>
        </bk-form>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import tools from '@/utils/tools.js'
    import BkUserSelector from '@blueking/user-selector'
    import { mapState, mapActions, mapMutations } from 'vuex'
    import { NAME_REG, STRING_LENGTH, INVALID_NAME_CHAR } from '@/constants/index.js'

    export default {
        name: 'BasicInfo',
        components: {
            BkUserSelector
        },
        props: {
            projectId: [String, Number],
            nodeConfig: Object,
            basicInfo: Object,
            versionList: Array,
            isSubflow: Boolean,
            formEnable: Boolean,
            inputLoading: Boolean,
            subflowUpdated: Boolean,
            common: [String, Number],
            isViewMode: Boolean
        },
        data () {
            return {
                labelData: [],
                labelLoading: false,
                subflowLoading: false,
                version: this.basicInfo.version,
                formData: tools.deepClone(this.basicInfo),
                maxNodeExecuteTimeout: window.MAX_NODE_EXECUTE_TIMEOUT,
                schemeList: [],
                schemeListLoading: false,
                pluginRules: {
                    plugin: [
                        {
                            required: true,
                            message: i18n.t('请选择插件'),
                            trigger: 'blur'
                        }
                    ],
                    version: [
                        {
                            required: true,
                            message: i18n.t('请选择插件版本'),
                            trigger: 'blur'
                        }
                    ],
                    nodeName: [
                        {
                            required: true,
                            message: i18n.t('节点名称不能为空'),
                            trigger: 'blur'
                        },
                        {
                            regex: NAME_REG,
                            message: i18n.t('节点名称不能包含') + INVALID_NAME_CHAR + i18n.t('非法字符'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH,
                            message: i18n.t('节点名称长度不能超过') + STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        }
                    ],
                    stageName: [
                        {
                            max: STRING_LENGTH.STAGE_NAME_MAX_LENGTH,
                            message: i18n.t('步骤名称长度不能超过') + STRING_LENGTH.STAGE_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        }
                    ]
                },
                subflowRules: {
                    tpl: [
                        {
                            required: true,
                            message: i18n.t('请选择流程模板'),
                            trigger: 'blur'
                        }
                    ],
                    nodeName: [
                        {
                            required: true,
                            message: i18n.t('节点名称不能为空'),
                            trigger: 'blur'
                        },
                        {
                            regex: NAME_REG,
                            message: i18n.t('节点名称不能包含') + INVALID_NAME_CHAR + i18n.t('非法字符'),
                            trigger: 'blur'
                        },
                        {
                            max: STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH,
                            message: i18n.t('节点名称长度不能超过') + STRING_LENGTH.TEMPLATE_NODE_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        }
                    ],
                    stageName: [
                        {
                            max: STRING_LENGTH.STAGE_NAME_MAX_LENGTH,
                            message: i18n.t('步骤名称长度不能超过') + STRING_LENGTH.STAGE_NAME_MAX_LENGTH + i18n.t('个字符'),
                            trigger: 'blur'
                        }
                    ]
                },
                errorHandleTipsConfig: {
                    allowHtml: true,
                    width: 400,
                    content: '#html-error-ingored-tootip',
                    placement: 'top'
                },
                userApi: `${window.MEMBER_SELECTOR_DATA_HOST}/api/c/compapi/v2/usermanage/fs_list_users/`
            }
        },
        computed: {
            ...mapState({
                'subprocessInfo': state => state.template.subprocess_info
            }),
            subflowHasUpdate () {
                if (!this.formData.alwaysUseLatest) {
                    return this.version !== this.basicInfo.version || this.subprocessInfo.details.some(subflow => {
                        if (
                            subflow.expired
                            && subflow.template_id === Number(this.formData.tpl)
                            && subflow.subprocess_node_id === this.nodeConfig.id
                        ) {
                            return true
                        }
                    })
                }
                return false
            },
            labelList () {
                if (this.labelLoading || this.labelData.length === 0) {
                    return []
                }
                return this.labelData.filter(groupItem => {
                    return !this.formData.nodeLabel.find(item => groupItem.code === item.group)
                })
            }
        },
        watch: {
            basicInfo (val, oldVal) {
                this.formData = tools.deepClone(val)
                if (val.tpl !== oldVal.tpl) {
                    this.getSubflowSchemeList()
                }
            }
        },
        created () {
            if (!this.isSubflow) { // 子流程节点不展示节点标签表单
                this.getNodeLabelList()
            } else {
                if (this.basicInfo.tpl) {
                    this.getSubflowSchemeList()
                }
            }
        },
        methods: {
            ...mapMutations('template/', [
                'setNodeBasicInfo'
            ]),
            ...mapActions('task', [
                'loadTaskScheme',
                'loadSubflowConfig'
            ]),
            ...mapActions('template/', [
                'getLabels'
            ]),
            // 加载子流程详情，拿到最新版本子流程的version字段
            async getSubflowDetail () {
                this.subflowLoading = true
                try {
                    const data = {
                        project_id: this.projectId,
                        template_id: this.basicInfo.tpl,
                        scheme_id_list: this.basicInfo.schemeIdList,
                        version: ''
                    }
                    if (this.common || this.nodeConfig.template_source === 'common') {
                        data.template_source = 'common'
                    } else {
                        data.project_id = this.projectId
                    }
                    const resp = await this.loadSubflowConfig(data)
                    this.version = resp.data.version
                } catch (e) {
                    console.log(e)
                } finally {
                    this.subflowLoading = false
                }
            },
            // 加载节点标签列表
            async getNodeLabelList () {
                try {
                    this.labelLoading = true
                    const resp = await this.getLabels()
                    this.labelData = this.transLabelListToGroup(resp.results)
                } catch (e) {
                    console.log(e)
                } finally {
                    this.labelLoading = false
                }
            },
            // 加载子流程对应的执行方案列表
            async getSubflowSchemeList () {
                try {
                    const data = {
                        project_id: this.projectId,
                        template_id: this.basicInfo.tpl,
                        isCommon: this.common || this.nodeConfig.template_source === 'common'
                    }
                    this.schemeList = await this.loadTaskScheme(data)
                    this.schemeListLoading = false
                } catch (e) {
                    console.log(e)
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
                    const group = this.labelData.find(g => g.code === item.group)
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
            openSelectorPanel () {
                if (this.isViewMode) return
                this.$emit('openSelectorPanel')
            },
            onLabelChange (list) {
                const val = []
                list.forEach(item => {
                    if (item.values && item.values.length > 0) {
                        val.push({
                            label: item.values[0].code,
                            group: item.code
                        })
                    }
                })
                this.formData.nodeLabel = val
                this.updateData()
            },
            onLabelClear () {
                this.formData.nodeLabel = []
                this.updateData()
            },
            onErrorHandlerChange (val, type) {
                this.formData.autoRetry.interval = 0
                this.formData.autoRetry.times = 1
                if (type === 'autoRetry') {
                    this.formData.autoRetry.enable = val
                    this.formData.retryable = true
                } else {
                    if (type === 'retryable') {
                        this.formData.autoRetry.enable = false
                        this.formData.autoRetry.interval = 0
                        this.formData.autoRetry.times = 1
                    }
                    if (type === 'ignorable' && val) {
                        this.formData.skippable = true
                        this.formData.retryable = false
                        this.formData.autoRetry.enable = false
                    }
                    this.formData[type] = val
                }
                if (val && ['autoRetry', 'ignorable'].includes(type)) {
                    this.formData.timeoutConfig = {
                        enable: false,
                        seconds: 10,
                        action: 'forced_fail'
                    }
                }
                this.updateData()
            },
            onTimeoutChange (val) {
                this.formData.timeoutConfig = {
                    enable: val,
                    seconds: 10,
                    action: 'forced_fail'
                }
                if (val) {
                    this.formData.ignorable = false
                    this.formData.autoRetry.enable = false
                }
                this.updateData()
            },
            onSelectableChange (val) {
                this.formData.selectable = val
                this.updateData()
            },
            onUserSelectChange (tags) {
                this.formData.executor_proxy = tags
                this.updateData()
            },
            async onAlwaysUseLatestChange (val) {
                this.formData.alwaysUseLatest = val
                if (!val) {
                    await this.getSubflowDetail()
                }
                this.updateData()
            },
            // 选择执行方案，需要更新子流程输入、输出参数
            onSelectTaskScheme (val) {
                this.formData.schemeIdList = val
                this.updateData()
                this.$emit('selectScheme', val)
            },
            updateData () {
                const {
                    version, nodeName, stageName, nodeLabel, ignorable, skippable, retryable,
                    selectable, alwaysUseLatest, autoRetry, timeoutConfig, schemeIdList, executor_proxy
                } = this.formData
                let data
                if (this.isSubflow) {
                    data = { nodeName, stageName, nodeLabel, selectable, alwaysUseLatest, schemeIdList, latestVersion: this.version, executor_proxy, retryable, autoRetry, timeoutConfig, skippable }
                } else {
                    data = { version, nodeName, stageName, nodeLabel, ignorable, skippable, retryable, selectable, autoRetry, timeoutConfig, executor_proxy }
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
    .disabled-search {
        position: relative;
        cursor: not-allowed;
        /deep/ .bk-search-select {
            border-color: #dcdee5 !important;
            background-color: #fafbfd !important;
        }
        &::after {
            content: '';
            height: 100%;
            width: 100%;
            position: absolute;
            top: 0;
            left: 0;
        }
    }
    .error-handle {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        height: 32px;
        /deep/ .bk-form-checkbox {
            &:not(:last-of-type) {
                margin-right: 8px;
            }
            &.is-disabled .bk-checkbox-text {
                color: #c4c6cc;
            }
            &.is-checked .bk-checkbox-text {
                color: #606266;
            }
        }
        .error-handle-icon {
            display: inline-block;
            line-height: 12px;
            color: #ffffff;
            background: #979ba5;
            border-radius: 2px;
            .text {
                display: inline-block;
                font-size: 12px;
                transform: scale(0.8);
            }
        }
        .auto-retry-times {
            display: inline-flex;
            align-items: center;
            margin-left: 4px;
            height: 32px;
            font-size: 12px;
            color: #606266;
        }
    }
    .error-handle-tips {
        font-size: 12px;
        line-height: 1;
        color: #ffb400;
    }
    .timeout-setting-wrap {
        display: flex;
        align-items: center;
        height: 32px;
        font-size: 12px;
        color: #63656e;
    }
    .number-input {
        position: relative;
        .unit {
            position: absolute;
            right: 8px;
            top: 1px;
            height: 30px;
            line-height: 30px;
            color: #999999;
            background: transparent;
        }
    }
    .auto-retry-times,
    .timeout-setting-wrap {
        /deep/ .bk-input-number .input-number-option {
            display: none;
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
            display: flex;
            margin-left: -1px;
            background: #e1ecff;
            border: none;
            z-index: 11;
        }
        .form-item-tips {
            position: absolute;
            left: -24px;
            top: 7px;
            color: #c4c6cc;
            &:hover {
                color: #f4aa1a;
            }
        }
        .view-subflow {
            display: flex;
            padding: 0 10px;
            justify-content: center;
            align-items: center;
            font-size: 12px;
            color: #63656e;
            background: #fafbfd;
            border-top: 1px solid #dcdee5;
            border-bottom: 1px solid #dcdee5;
            cursor: pointer;
            &:hover {
                color: #3a84ff;
            }
        }
        .operate-btn {
            display: inline-block;
            width: 58px;
            height: 32px;
            line-height: 32px;
            font-size: 12px;
            color: #3a84ff;
            text-align: center;
            border: 1px solid #3a84ff;
            cursor: pointer;
            &.is-disabled {
                border-color: #c4c6cc;
                color: #c4c6cc;
                cursor: not-allowed;
            }
        }
        .choose-plugin-input {
            .bk-form-input[readonly] {
                border-color: #c4c6cc !important;
            }
        }
        .plugin-info-desc {
            margin-top: 8px;
            font-size: 12px;
            color: #ff9c01;
            line-height: 1.2;
        }
        .update-tooltip {
            position: relative;
            top: 5px;
            color: #979ba5;
            font-size: 12px;
            line-height: 12px;
            .bk-button-text {
                font-size: 12px;
            }
        }
        .user-selector {
            width: 100%;
            .disabled::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                height: 100%;
                width: 100%;
                cursor: not-allowed;
            }
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
