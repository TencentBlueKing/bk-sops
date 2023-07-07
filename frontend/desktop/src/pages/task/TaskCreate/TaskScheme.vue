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
            <bk-alert type="info" class="single-use-alert">
                <template slot="title">
                    <i18n tag="div" path="singleUseTips">
                        <span class="single-use" @click="onImportTemporaryPlan">{{ $t('一次性方案') }}</span>
                    </i18n>
                </template>
            </bk-alert>
            <div class="scheme-content" data-test-id="createTask_form_schemeList">
                <p :class="['scheme-title', { 'data-empty': !schemeList.length && !nameEditing }]">
                    <bk-checkbox
                        :value="isAllChecked"
                        :indeterminate="indeterminate"
                        :disabled="!schemeList.length"
                        @change="onAllCheckChange">
                    </bk-checkbox>
                    <span class="scheme-name">{{ $t('方案名称') }}</span>
                </p>
                <ul class="scheme-list" v-if="schemeList.length || nameEditing">
                    <li
                        v-for="item in schemeList"
                        class="scheme-item"
                        :class="{ 'is-checked': Boolean(planDataObj[item.uuid]) }"
                        :key="item.uuid">
                        <bk-checkbox
                            :value="Boolean(planDataObj[item.uuid])"
                            @change="onCheckChange($event, item)">
                        </bk-checkbox>
                        <span class="scheme-name" :title="item.name">{{item.name}}</span>
                        <span v-if="item.isDefault" class="default-label">{{$t('默认')}}</span>
                    </li>
                </ul>
                <!-- 无数据提示 -->
                <NoData v-else></NoData>
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
            isPreviewMode: {
                type: Boolean,
                default: false
            },
            selectedNodes: {
                type: Array,
                default () {
                    return []
                }
            },
            planDataObj: {
                type: Object,
                default: () => {}
            },
            excludeNode: {
                type: Array,
                default () {
                    return []
                }
            },
            orderedNodeData: {
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
                defaultIdList: [],
                defaultSchemeId: null
            }
        },
        computed: {
            ...mapState('project', {
                'projectName': state => state.projectName
            }),
            isAllChecked () {
                const selectPlanLength = Object.keys(this.planDataObj).length
                return selectPlanLength && selectPlanLength === this.schemeList.length
            },
            indeterminate () {
                const selectPlanLength = Object.keys(this.planDataObj).length
                return Boolean(selectPlanLength) && selectPlanLength !== this.schemeList.length
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
            onCheckChange (e, scheme) {
                this.$emit('selectScheme', scheme, e)
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
                    const defaultObj = {}
                    this.schemeList.forEach(scheme => {
                        this.$set(scheme, 'isDefault', false)
                        this.$set(scheme, 'uuid', scheme.id)
                        if (this.defaultIdList.includes(scheme.uuid)) {
                            scheme.isDefault = true
                            defaultObj[scheme.uuid] = JSON.parse(scheme.data)
                        }
                    })
                    this.$emit('updateTaskSchemeList', this.schemeList, false)
                    this.$emit('setDefaultScheme', defaultObj)
                    this.$emit('setDefaultSelected', false)
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
                        const { id, scheme_ids: schemeIds } = resp.data[0]
                        this.defaultSchemeId = id
                        this.defaultIdList = schemeIds
                    }
                } catch (error) {
                    console.warn(error)
                }
            },
            /**
             * 执行方案全选/半选
             */
            onAllCheckChange (val) {
                this.$emit('selectAllScheme', val)
            },
            /**
             * 任务方案面板是否显示
             */
            toggleSchemePanel () {
                this.showPanel = !this.showPanel
            },
            /**
             * 导入临时方案
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
        width: 640px;
        height: 100%;
        padding: 0 24px;
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
            font-size: 16px;
            color: #313238;
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
        .single-use-alert {
            margin: 10px 0 15px 0;
            .single-use {
                color: #3a84ff;
                cursor: pointer;
            }
        }
        .scheme-content {
            max-height: calc(100% - 127px);
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
</style>
