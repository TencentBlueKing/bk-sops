<template>
    <div class="basic-info">
        <!--普通插件-->
        <bk-form
            v-if="!isSubFlow"
            ref="pluginForm"
            form-type="vertical"
            :model="formData"
            :rules="pluginRules">
            <bk-form-item :label="$t('标准插件')" :required="true" property="plugin" class="choose-plugin-input">
                <bk-input :value="formData.name" readonly>
                    <template slot="append">
                        <i :class="['bk-icon icon-sort', { 'is-disabled': isViewMode }]" @click="openSelectorPanel"></i>
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
                <bk-input
                    :readonly="isViewMode"
                    v-model="formData.nodeName"
                    :maxlength="stringLength.TEMPLATE_NODE_NAME_MAX_LENGTH"
                    :show-word-limit="true"
                    @change="updateData">
                </bk-input>
            </bk-form-item>
            <bk-form-item :label="$t('步骤名称')" data-test-id="templateEdit_form_stageName" property="stageName">
                <bk-input
                    :readonly="isViewMode"
                    v-model="formData.stageName"
                    :maxlength="stringLength.STAGE_NAME_MAX_LENGTH"
                    :show-word-limit="true"
                    @change="updateData">
                </bk-input>
            </bk-form-item>
        </bk-form>
        
        <!-- 子流程 -->
        <bk-form
            v-else
            ref="subFlowForm"
            form-type="vertical"
            :model="formData"
            :rules="subFlowRules">
            <bk-form-item :label="$t('流程模板')" :required="true" property="tpl">
                <bk-input :value="formData.name" readonly>
                    <template slot="append">
                        <div
                            v-if="basicInfo.tpl"
                            class="view-sub-flow"
                            @click="$emit('viewSubFlow', basicInfo.tpl)">
                            <i class="bk-icon common-icon-box-top-right-corner"></i>
                        </div>
                        <i :class="['bk-icon icon-sort', { 'is-disabled': isViewMode }]"></i>
                    </template>
                </bk-input>
                <!-- 子流程版本更新 -->
                <p class="update-tooltip" v-if="!inputLoading && subFlowHasUpdate && !subFlowUpdated">
                    {{ $t('子流程有更新，更新时若存在相同表单数据则获取原表单的值。') }}
                    <bk-button :text="true" title="primary" :disabled="isViewMode" @click="onUpdateSubFlowVersion">{{ $t('更新子流程') }}</bk-button>
                </p>
            </bk-form-item>
            <bk-form-item :label="$t('总是使用最新版本')">
                <bk-switcher
                    theme="primary"
                    size="small"
                    :disabled="isViewMode"
                    :value="formData.alwaysUseLatest"
                    @change="onAlwaysUseLatestChange">
                </bk-switcher>
            </bk-form-item>
            <bk-form-item :label="$t('节点名称')" :required="true" property="nodeName">
                <bk-input
                    :readonly="isViewMode"
                    v-model="formData.nodeName"
                    :maxlength="stringLength.TEMPLATE_NODE_NAME_MAX_LENGTH"
                    :show-word-limit="true"
                    @change="updateData">
                </bk-input>
            </bk-form-item>
            <bk-form-item :label="$t('步骤名称')" property="stageName">
                <bk-input
                    :readonly="isViewMode"
                    v-model="formData.stageName"
                    :maxlength="stringLength.STAGE_NAME_MAX_LENGTH"
                    :show-word-limit="true"
                    @change="updateData">
                </bk-input>
            </bk-form-item>
            <bk-form-item
                :label="$t('执行方案')"
                :desc="{
                    theme: 'light',
                    extCls: 'info-label-tips',
                    placement: 'top-start',
                    content: $t('每次创建任务会使用选中执行方案的最新版本且不会提示该节点需要更新')
                }">
                <bk-select
                    :value="formData.schemeIdList"
                    :clearable="false"
                    :multiple="true"
                    :loading="schemeListLoading"
                    :placeholder="inputLoading || schemeListLoading || schemeList.length ? $t('请选择') : $t('此流程无执行方案，无需选择')"
                    :disabled="isViewMode || inputLoading || schemeListLoading || !schemeList.length"
                    @selected="onSelectTaskScheme">
                    <bk-option v-for="item in schemeList" :key="item.id" :id="item.id" :name="item.name"></bk-option>
                </bk-select>
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
    // import BkUserSelector from '@blueking/user-selector'
    import { mapActions, mapGetters } from 'vuex'
    import { NAME_REG, STRING_LENGTH, INVALID_NAME_CHAR } from '@/constants/index.js'
    export default {
        name: 'BasicInfo',
        props: {
            project_id: [String, Number],
            nodeConfig: Object,
            basicInfo: Object,
            versionList: Array,
            isSubFlow: Boolean,
            inputLoading: Boolean,
            subFlowUpdated: Boolean,
            common: [String, Number],
            isViewMode: Boolean
        },
        data () {
            return {
                formData: tools.deepClone(this.basicInfo),
                schemeList: [],
                schemeListLoading: true,
                stringLength: STRING_LENGTH,
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
                subFlowRules: {
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
                userApi: `${window.MEMBER_SELECTOR_DATA_HOST}/api/c/compapi/v2/usermanage/fs_list_users/`,
                subFlowLoading: false
            }
        },
        computed: {
            subFlowHasUpdate () {
                if (!this.formData.alwaysUseLatest) {
                    return this.version !== this.basicInfo.version || this.subprocessInfo.details.some(item => {
                        if (
                            item.expired
                            && item.template_id === Number(this.formData.tpl)
                            && item.subprocess_node_id === this.nodeConfig.id
                        ) {
                            return true
                        }
                    })
                }
                return false
            }
        },
        watch: {
            basicInfo (val, oldVal) {
                this.formData = tools.deepClone(val)
                // 如果有执行方案，默认选中<不使用执行方案>
                if (this.schemeList.length && !this.formData.schemeIdList.length) {
                    this.formData.schemeIdList = [0]
                }
                if (val.tpl !== oldVal.tpl) {
                    this.getSubFlowSchemeList()
                }
            }
        },
        methods: {
            ...mapActions('task', [
                'loadTaskScheme',
                'loadSubflowConfig'
            ]),
            ...mapGetters('template/', [
                'getPipelineTree'
            ]),
            
            // 加载子流程详情，拿到最新版本子流程的version字段
            async getSubFlowDetail () {
                this.subFlowLoading = true
                try {
                    const data = {
                        project_id: this.project_id,
                        template_id: this.basicInfo.tpl,
                        scheme_id_list: this.basicInfo.schemeIdList,
                        version: ''
                    }
                    if (this.common || this.nodeConfig.template_source === 'common') {
                        data.template_source = 'common'
                    } else {
                        data.project_id = this.project_id
                    }
                    const resp = await this.loadSubflowConfig(data)
                    this.version = resp.data.version
                } catch (e) {
                    console.log(e)
                } finally {
                    this.subFlowLoading = false
                }
            },
            // 加载子流程对应的执行方案列表
            async getSubFlowSchemeList () {
                try {
                    const data = {
                        project_id: this.project_id,
                        template_id: this.basicInfo.tpl,
                        isCommon: this.common || this.nodeConfig.template_source === 'common'
                    }
                    this.schemeList = await this.loadTaskScheme(data)
                    // 添加<不使用执行方案>,如果没有选择方案时默认选中
                    const { activities = {} } = this.getPipelineTree()
                    const nodeList = Object.keys(activities)
                    if (this.schemeList.length) {
                        this.schemeList.unshift({
                            data: JSON.stringify(nodeList),
                            id: 0,
                            name: '<' + i18n.t('不使用执行方案') + '>'
                        })
                        if (!this.formData.schemeIdList.length) {
                            this.formData.schemeIdList = [0]
                        }
                    }
                    this.schemeListLoading = false
                } catch (e) {
                    console.log(e)
                }
            },
            openSelectorPanel () {
                if (this.isViewMode) return
                this.$emit('openSelectorPanel')
            },
            onUserSelectChange (tags) {
                this.formData.executor_proxy = tags
                this.updateData()
            },
            // 选择执行方案，需要更新子流程输入、输出参数
            onSelectTaskScheme (val, options) {
                // 切换执行方案时取消<不使用执行方案>
                const lastId = options.length ? options[options.length - 1].id : undefined
                val = lastId === 0 ? [0] : lastId ? val.filter(id => id) : val
                this.formData.schemeIdList = val
                this.updateData()
                this.$emit('selectScheme', val)
            },
            /**
             * 子流程版本更新
             */
            onUpdateSubFlowVersion () {
                if (this.inputLoading) {
                    return
                }

                this.$emit('updateSubFlowVersion')
            },
            async onAlwaysUseLatestChange (val) {
                this.formData.alwaysUseLatest = val
                if (!val) {
                    await this.getSubFlowDetail()
                }
                this.updateData()
            },
            updateData () {
                const { version, nodeName, stageName, nodeLabel, selectable, schemeIdList, executor_proxy, alwaysUseLatest } = this.formData
                let data
                if (this.isSubFlow) {
                    data = { nodeName, stageName, nodeLabel, selectable, schemeIdList, latestVersion: this.version, executor_proxy, alwaysUseLatest }
                } else {
                    data = { version, nodeName, stageName, nodeLabel, selectable, executor_proxy }
                }
                this.$emit('update', data)
            },
            validate () {
                const comp = this.isSubFlow ? this.$refs.subFlowForm : this.$refs.pluginForm
                comp.clearError()
                return comp.validate()
            }
        }
    }
</script>

<style lang="scss" scoped>
.basic-info {
    padding: 16px 30px 32px;
    /deep/ .bk-form {
        .bk-form-item:not(:first-child) {
            margin-top: 24px;
        }
        .bk-label {
            min-height: 20px;
            line-height: 20px;
            margin-bottom: 6px;
        }
        .bk-form-control .group-box.group-append {
            display: flex;
            margin-left: -1px;
            background: #e1ecff;
            border: none;
            z-index: 11;
        }
        .group-append {
            margin-left: -1px;
            border: none;
            .icon-sort {
                display: inline-block;
                width: 32px;
                height: 32px;
                line-height: 32px;
                text-align: center;
                font-size: 14px;
                color: #3a84ff;
                background: #e1ecff;
                border: 1px solid #1768ef;
                transform: rotate(90deg);
                cursor: pointer;
                &.is-disabled {
                    color: #c4c6cc;
                    background: #f0f1f5;
                    border-color: #dcdee5;
                    cursor: not-allowed;
                }
            }
        }
    }
    .view-sub-flow {
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
</style>
