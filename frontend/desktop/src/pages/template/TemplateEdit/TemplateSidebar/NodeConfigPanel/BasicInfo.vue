<template>
    <div class="basic-info">
        <!--普通插件-->
        <bk-form
            v-if="!isSubFlow"
            ref="pluginForm"
            form-type="vertical"
            :model="formData"
            :rules="pluginRules">
            <bk-form-item
                :label="$t('标准插件')"
                :required="true"
                property="plugin"
                class="choose-plugin-input"
                :error-display-type="'normal'"
                :rules="isNotExist ? [] : pluginRules.plugin">
                <bk-input :value="formData.name" readonly :key="basicInfo.plugin" :class="{ 'is-active': isSelectorPanelShow }">
                    <template slot="prepend" v-if="isThirdParty">
                        <span class="third-mark-prepend">{{ $t('第三方') }}</span>
                    </template>
                    <div slot="append" style="display: flex">
                        <p v-if="basicInfo.plugin_contact" class="third-plugin-contact">
                            {{ $t('由') + ' ' + basicInfo.plugin_contact + ' ' + $t('提供') }}
                        </p>
                        <i :class="['bk-icon icon-sort append-icon', { 'is-disabled': isViewMode && !isNotExist }]" @click="openSelectorPanel"></i>
                    </div>
                </bk-input>
                <p v-if="formData.desc" class="plugin-info-desc" v-html="formData.desc"></p>
                <p v-if="isNotExist" class="plugin-info-desc">{{ $t('插件已失效，请重新选择') }}</p>
            </bk-form-item>
            <template v-if="basicInfo.plugin && !isNotExist">
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
            </template>
        </bk-form>
        
        <!-- 子流程 -->
        <bk-form
            v-else
            ref="subFlowForm"
            form-type="vertical"
            :model="formData"
            :rules="subFlowRules">
            <bk-form-item :label="$t('流程模板')" :required="true" property="tpl">
                <TplSelect
                    :value="formData.tpl"
                    :is-view-mode="isViewMode"
                    :project_id="project_id"
                    :common="common"
                    :node-config="nodeConfig"
                    @select="$emit('select', $event)">
                </TplSelect>
                <p
                    v-if="basicInfo.tpl"
                    class="view-sub-flow"
                    @click="onViewSubFlow(basicInfo.tpl)">
                    <i class="bk-icon common-icon-box-top-right-corner"></i>
                    {{ $t('查看子流程') }}
                </p>
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
            <template v-if="basicInfo.tpl">
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
            </template>
        </bk-form>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import tools from '@/utils/tools.js'
    import permission from '@/mixins/permission.js'
    import { mapState, mapActions, mapGetters } from 'vuex'
    import { NAME_REG, STRING_LENGTH, INVALID_NAME_CHAR } from '@/constants/index.js'
    import TplSelect from './TplSelect.vue'
    export default {
        name: 'BasicInfo',
        components: {
            TplSelect
        },
        mixins: [permission],
        props: {
            project_id: [String, Number],
            nodeConfig: Object,
            basicInfo: Object,
            versionList: Array,
            isSubFlow: Boolean,
            isThirdParty: Boolean,
            inputLoading: Boolean,
            subFlowUpdated: Boolean,
            common: [String, Number],
            isViewMode: Boolean,
            isSelectorPanelShow: Boolean,
            isNotExist: Boolean
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
                version: this.basicInfo.version,
                subFlowLoading: false
            }
        },
        computed: {
            ...mapState({
                'subprocessInfo': state => state.template.subprocess_info
            }),
            subFlowHasUpdate () {
                if (!this.formData.alwaysUseLatest) {
                    return this.version !== this.basicInfo.version || this.subprocessInfo?.details.some(item => {
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
                if (val.tpl && val.tpl !== oldVal.tpl) {
                    this.version = val.version
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
                if (this.isViewMode && !this.isNotExist) return
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
            },
            // 查看子流程模板
            onViewSubFlow (id) {
                const { name } = this.$route
                const routerName = name === 'commonTemplatePanel'
                    ? 'commonTemplatePanel'
                    : this.isCommonTpl
                        ? 'projectCommonTemplatePanel'
                        : 'templatePanel'
                const pathData = {
                    name: routerName,
                    params: {
                        type: 'view',
                        project_id: name === 'commonTemplatePanel' ? undefined : this.project_id
                    },
                    query: {
                        template_id: id,
                        common: name === 'templatePanel' ? undefined : '1'
                    }
                }
                const { href } = this.$router.resolve(pathData)
                window.open(href, '_blank')
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
        .choose-plugin-input {
            .group-prepend {
                flex-shrink: 0;
                display: flex;
                align-items: center;
                border-color: #dcdee5;
                background: #fafbfd;
                .third-mark-prepend {
                    font-size: 12px;
                    transform: scale(0.83);
                    line-height: 16px;
                    padding: 2px 4px;
                    margin: 1px -8px 0 2px;
                    color: #14a586;
                    background: #e4faf0;
                    border-radius: 2px;
                }
                & + .bk-input-text {
                    input {
                        border-left: none;
                    }
                }
            }
            .bk-form-input  {
                color: #63656e !important;
            }
            .bk-form-control .group-box.group-append {
                display: flex;
                margin-left: -1px;
                background: #e1ecff;
                border: none;
                z-index: 11;
            }
            .group-append {
                flex-shrink: 0;
                margin-left: -1px;
                border: none;
                .third-plugin-contact {
                    font-size: 12px;
                    line-height: 30px;
                    color: #979ba5;
                    padding-right: 8px;
                    border-top: 1px solid #dcdee5;
                    border-bottom: 1px solid #dcdee5;
                    background: #fafbfd;
                }
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
            .is-active {
                .group-prepend,
                .bk-form-input,
                .third-plugin-contact {
                    border-color: #3a84ff !important;
                }
            }
        }
    }
    .bk-select-inline {
        width: 100%;
    }
    .view-sub-flow {
        position: absolute;
        right: 0;
        top: -26px;
        display: flex;
        line-height: 20px;
        font-size: 12px;
        color: #3a84ff;
        cursor: pointer;
        i {
            margin: 5px 6px 0 0;
        }
    }
    .plugin-info-desc {
        margin-top: 8px;
        font-size: 12px;
        color: #ff9c01;
        line-height: 1.2;
    }
    .update-tooltip {
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
