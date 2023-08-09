<template>
    <div class="task-scheme" v-if="isSchemeShow">
        <div class="scheme-nav" @click="toggleSchemePanel">
            <i class="bk-icon icon-angle-left"></i>
            <span>{{ $t('执行方案') }}</span>
        </div>
        <div class="scheme-list-panel" v-if="showPanel">
            <div class="scheme-sideslider-header">
                <span>{{$t('执行方案')}}</span>
                <i @click="toggleSchemePanel" class="bk-icon icon-close-line"></i>
            </div>
            <div class="scheme-active-wrapper" v-if="viewMode !== 'appmaker'">
                <bk-button
                    :text="true"
                    :class="{ 'text-permission-disable': !hasOperateSchemeTpl }"
                    v-cursor="{ active: !hasOperateSchemeTpl }"
                    @click="goManageScheme">
                    <i class="common-icon-box-top-right-corner"></i>
                    {{ $t('管理执行方案') }}
                </bk-button>
                <bk-button :text="true" class="ml20" @click="onImportTemporaryPlan">
                    <i class="common-icon-batch-select"></i>
                    {{ $t('使用临时方案') }}
                </bk-button>
            </div>
            <div class="scheme-content" data-test-id="createTask_form_schemeList">
                <p :class="['scheme-title', { 'data-empty': !schemeList.length }]">
                    <bk-checkbox
                        :value="isAllChecked"
                        :indeterminate="indeterminate"
                        :disabled="!schemeList.length"
                        @change="onAllCheckChange">
                    </bk-checkbox>
                    <span class="scheme-name">{{ $t('方案名称') }}</span>
                </p>
                <ul class="scheme-list" v-if="schemeList.length">
                    <li
                        v-for="item in schemeList"
                        class="scheme-item"
                        :class="{ 'is-checked': item.isChecked }"
                        :key="item.id">
                        <bk-checkbox
                            :value="item.isChecked"
                            @change="onCheckChange(item)">
                        </bk-checkbox>
                        <span class="scheme-name" :title="item.name">{{item.name}}</span>
                        <i
                            v-if="item.isDefault"
                            v-bk-tooltips="{ content: $t('默认方案'), boundary: 'window' }"
                            :class="['common-icon-default', { 'is-default': item.isDefault }]">
                        </i>
                    </li>
                </ul>
                <!-- 无数据提示 -->
                <NoData v-else :message="$t('暂无方案')">
                    <p style="margin-top: 8px">
                        <bk-button
                            :text="true"
                            :class="{ 'text-permission-disable': !hasOperateSchemeTpl }"
                            v-cursor="{ active: !hasOperateSchemeTpl }"
                            @click="goManageScheme">
                            {{ $t('前往新增方案') }}
                        </bk-button>
                        <bk-button :text="true" @click="onImportTemporaryPlan" class="ml15">
                            {{ $t('使用临时方案') }}
                        </bk-button>
                    </p>
                </NoData>
            </div>
        </div>
    </div>
</template>
<script>
    import { mapState, mapActions } from 'vuex'
    import permission from '@/mixins/permission.js'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'TaskScheme',
        components: {
            NoData
        },
        mixins: [permission],
        props: {
            template_id: {
                type: [String, Number],
                default: ''
            },
            templateName: {
                type: String,
                default: ''
            },
            project_id: {
                type: [String, Number],
                default: ''
            },
            isCommonProcess: {
                type: Boolean,
                default: false
            },
            isSchemeShow: {
                type: Boolean,
                default: false
            },
            viewMode: {
                type: String,
                default: ''
            },
            isSchemeEditable: {
                type: Boolean,
                default: false
            },
            isPreviewMode: {
                type: Boolean,
                default: false
            },
            orderedNodeData: {
                type: Array,
                default () {
                    return []
                }
            },
            tplActions: {
                type: Array,
                default () {
                    return []
                }
            }
        },
        data () {
            return {
                showPanel: false,
                schemeList: [],
                defaultSchemeList: []
            }
        },
        computed: {
            ...mapState('project', {
                'projectId': state => state.project_id,
                'projectName': state => state.projectName
            }),
            isAllChecked () {
                return this.schemeList.every(item => item.isChecked)
            },
            indeterminate () {
                return !this.isAllChecked && this.schemeList.some(item => item.isChecked)
            },
            hasOperateSchemeTpl () {
                const tplAction = this.isCommonProcess ? 'common_flow_edit' : 'flow_edit'
                return this.hasPermission([tplAction], this.tplActions)
            }
        },
        created () {
            this.initLoad()
        },
        methods: {
            ...mapActions('task/', [
                'loadTaskScheme',
                'getDefaultTaskScheme'
            ]),
            // 选择方案并进行切换更新选择的节点
            onCheckChange (scheme) {
                scheme.isChecked = !scheme.isChecked
                this.$emit('selectScheme')
            },
            async initLoad () {
                try {
                    await this.loadDefaultSchemeList()
                    this.loadSchemeList()
                } catch (error) {
                    console.warn(error)
                }
            },
            // 获取方案列表
            async loadSchemeList () {
                try {
                    this.schemeList = await this.loadTaskScheme({
                        project_id: this.project_id,
                        template_id: this.template_id,
                        isCommon: this.isCommonProcess
                    }) || []
                    let selectNodes = []
                    this.schemeList.forEach(scheme => {
                        this.$set(scheme, 'isChecked', false)
                        this.$set(scheme, 'isDefault', false)
                        if (this.defaultSchemeList.includes(scheme.id)) {
                            scheme.isDefault = true
                            scheme.isChecked = true
                            selectNodes.push(...JSON.parse(scheme.data))
                        }
                    })
                    selectNodes = Array.from(new Set(selectNodes)) || []
                    this.$emit('setCanvasSelected', selectNodes)
                } catch (e) {
                    console.log(e)
                }
            },
            // 获取默认方案列表
            async loadDefaultSchemeList () {
                try {
                    const resp = await this.getDefaultTaskScheme({
                        project_id: this.isCommonProcess ? undefined : this.project_id,
                        template_type: this.isCommonProcess ? 'common' : undefined,
                        template_id: Number(this.template_id)
                    })
                    if (resp.data.length) {
                        const { scheme_ids: schemeIds } = resp.data[0]
                        this.defaultSchemeList = schemeIds
                    }
                } catch (error) {
                    console.warn(error)
                }
            },
            /**
             * 执行方案全选/半选
             */
            onAllCheckChange (val) {
                this.schemeList.forEach(scheme => {
                    scheme.isChecked = val
                })
                this.$emit('selectAllScheme', val)
            },
            /**
             * 任务方案面板是否显示
             */
            toggleSchemePanel () {
                this.showPanel = !this.showPanel
            },
            goManageScheme () {
                const tplAction = this.isCommonProcess ? 'common_flow_edit' : 'flow_edit'
                const hasPermission = this.checkSchemeRelativePermission([tplAction])

                if (!hasPermission) return
                const { href } = this.$router.resolve({
                    name: 'templatePanel',
                    params: { type: 'edit' },
                    query: { template_id: this.template_id, manageScheme: true }
                })
                window.open(href, '_blank')
                // 监听浏览器切换事件
                document.addEventListener('visibilitychange', this.handleVisibilitychange)
            },
            /**
             * 校验权限，若无权限弹出权限申请弹窗
             * @params {Array} required 被校验的权限
             */
            checkSchemeRelativePermission (required) {
                if (!this.hasPermission(required, this.tplActions)) {
                    const flowType = this.isCommonProcess ? 'common_flow' : 'flow'
                    const resourceData = {
                        [`${flowType}`]: [{
                            id: this.template_id,
                            name: this.templateName
                        }],
                        project: [{
                            id: this.projectId,
                            name: this.projectName
                        }]
                    }
                    this.applyForPermission(required, this.tplActions, resourceData)
                    return false
                }
                return true
            },
            handleVisibilitychange () {
                if (document.visibilityState !== 'hidden') {
                    document.removeEventListener('visibilitychange', this.handleVisibilitychange)
                    // 更新执行列表
                    this.initLoad()
                }
            },
            /**
             * 临时方案
            */
            onImportTemporaryPlan () {
                this.$emit('onImportTemporaryPlan')
            }
        }
    }
</script>>
<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    @import '@/scss/config.scss';

    .task-scheme {
        position: absolute;
        top: 0;
        right: 0;
        height: 100%;
    }
    .scheme-list-panel {
        position: absolute;
        top: 0;
        right: 0;
        width: 520px;
        height: 100%;
        display: flex;
        flex-direction: column;
        background: $whiteDefault;
        border-left: 1px solid $commonBorderColor;
        box-shadow: 0 0 8px rgba(0, 0, 0, 0.15);
        z-index: 5;
        transition: right 0.5s ease-in-out;
        .scheme-sideslider-header {
            height: 54px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            font-size: 16px;
            color: #313238;
            box-shadow: inset 0 -1px 0 0 #DCDEE5;
            .icon-close-line {
                color: #63656e;
                font-size: 14px;
                font-weight: 600;
                margin-right: 3px;
                cursor: pointer;
                &:hover {
                    color: #3a84ff;
                }
            }
        }
        .scheme-active-wrapper {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            margin: 12px 24px 0;
            font-size: 14px;
            /deep/.bk-button-text i {
                font-size: 12px;
                margin-right: 3px;
                vertical-align: middle;
            }
        }
        .single-use-alert {
            margin: 10px 0 15px 0;
            .single-use {
                color: #3a84ff;
                cursor: pointer;
            }
        }
        .scheme-content {
            max-height: calc(100% - 127px);
            margin: 16px 24px 0;
            border: 1px solid #dee0e6;
            .scheme-title, .scheme-item {
                position: relative;
                height: 42px;
                display: flex;
                align-items: center;
                font-size: 12px;
                padding-left: 16px;
                border-bottom: 1px solid #ebebeb;
            }
            .scheme-list {
                height: calc(100% - 41px);
                overflow: hidden;
                overflow-y: auto;
                @include scrollbar;
            }
            .scheme-name {
                max-width: 400px;
                margin-left: 10px;
                overflow: hidden;
                white-space: nowrap;
                text-overflow: ellipsis;
                color: #313238;
            }
            .default-label {
                height: 22px;
                line-height: 22px;
                font-size: 12px;
                padding: 0 10px;
                border-radius: 2px;
                margin-left: 10px;
                color: #14a568;
                background: #e4faf0;
            }
            .common-icon-default {
                position: absolute;
                top: 15px;
                right: 10px;
                font-size: 14px;
                margin-top: 1px;
                color: #979ba5;
                font-weight: 500;
                &:hover {
                    color: #3a84ff !important;
                }
                &.is-default {
                    color: #3a84ff;
                }
            }
            .scheme-title {
                background: #fafbfd;
            }
            .scheme-item {
                &:hover {
                    background: #f0f1f5;
                }
                &.is-checked {
                    background: #eaf3ff;
                }
                &:last-child {
                    border-bottom: none;
                }
            }
        }
        .scheme-preview-mode {
            position: relative;
            width: 420px;
            .scheme-header-division-line-last {
                margin: 0 25px 0 20px;
                border: 0;
                height: 1px;
                background-color:#cacedb;
            }
            .preview-mode-switcher {
                position: relative;
                top: 19px;
                left: 20px;
                span {
                    font-size: 14px;
                    font-weight: 400;
                    color: #313238;
                }
            }
        }
    }
    .scheme-nav {
        position: absolute;
        right: 0;
        top: 20px;
        display: flex;
        align-items: center;
        width: 72px;
        z-index: 5;
        background: #fafbfd;
        border: 1px solid #3a84ff;
        border-right: none;
        border-radius: 12px 0px 0px 12px;
        font-size: 12px;
        line-height: 22px;
        vertical-align: middle;
        color: #3a84ff;
        cursor: pointer;
        .bk-icon {
            font-size: 16px;
            position: relative;
            left: 4px;
            top: 1px;
            margin-right: 3px;
        }
    }
    .disable-item {
        cursor: not-allowed;
        &:hover {
            background: inherit ;
        }
    }
    .scheme-name-wrapper {
        padding: 10px 0;
        label {
            float: left;
            margin-top: 6px;
            width: 100px;
            text-align: right;
        }
        .scheme-name-input {
            margin: 0 35px 0 120px;
        }
    }
    .no-data-wrapper {
        height: auto;
        padding: 22px 0 32px;
    }
</style>
