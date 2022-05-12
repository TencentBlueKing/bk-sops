/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <!-- 容器 -->
    <div class="page-view">
        <!-- 信息 -->
        <section class="bk-block">
            <van-cell>
                <template slot="title">
                    <div class="bk-text">{{ templateData.name }}</div>
                    <div class="bk-name">{{ templateData.creator_name }}</div>
                    <div class="bk-time">{{ templateData.create_time }}</div>
                </template>
                <van-icon
                    slot="right-icon"
                    name="star"
                    :class="['star-icon', collected ? 'collection' : '']"
                    @click="collect" />
            </van-cell>
        </section>
        <!-- 任务信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">{{ i18n.taskInfo }}</h2>
            <div class="bk-text-list">
                <van-field
                    :label="i18n.taskName"
                    name="taskName"
                    v-validate="taskNameRule"
                    :error="errors.has('taskName')"
                    :error-message="errors.first('taskName')"
                    v-model="taskName" />
                <van-cell
                    :title="i18n.scheme"
                    :value="scheme"
                    @click="show = true" />
                <van-cell>
                    <router-link :to="`/template/preview?templateId=${templateId}`">{{ i18n.canvasPreview }}</router-link>
                </van-cell>
            </div>
        </section>
        <!-- 方案选择popup -->
        <van-popup
            v-model="show"
            position="bottom"
            :overlay="true">
            <van-picker
                show-toolbar
                :columns="columns"
                :default-index="defaultSchemaIndex"
                @confirm="onConfirm"
                @cancel="show = false" />
        </van-popup>

        <!-- 日期选择popup -->
        <van-popup
            v-model="dateTimeShow"
            position="bottom"
            :overlay="true">
            <van-datetime-picker
                type="datetime"
                show-toolbar
                v-model="currentDate"
                @confirm="onDateTimeConfirm"
                @cancel="onDateTimeCancel" />
        </van-popup>

        <!-- 参数信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">{{ i18n.paramInfo }}</h2>
            <div class="bk-text-list">
                <template v-if="Object.keys(templateConstants).length">
                    <template v-if="!loadingConfig">
                        <template v-for="item in sortedConstants">
                            <VantComponent
                                v-if="!loadingConfig && item.show_type === 'show'"
                                :source-code="item.source_tag"
                                :custom-type="item.custom_type"
                                :key="item.key"
                                :label="item.name"
                                :placeholder="i18n.paramInput"
                                :value="item.value"
                                :data="item"
                                :render-config="item.renderConfig"
                                @dataChange="onInputDataChange" />
                        </template>
                    </template>
                    <div v-else class="holder-wrap">
                        <van-loading type="spinner" size="24" />
                    </div>
                </template>
                <div v-else class="holder-wrap">
                    <no-data />
                </div>
            </div>
        </section>
        <div class="btn-group">
            <van-button
                v-if="creating"
                loading
                disabled
                :loading-text="`${i18n.btnCreate}...`"
                size="large"
                type="info" />
            <van-button
                v-else
                size="large"
                type="info"
                :disabled="loadingConfig"
                @click="onCreateClick">{{ i18n.btnCreate }}</van-button>
        </div>

    </div>
</template>

<script>
    import { NAME_REG } from '@/constants/index.js'
    import moment from 'moment'
    import { mapActions, mapState } from 'vuex'
    import { dateFormatter } from '@/common/util.js'
    import NoData from '@/components/NoData/index.vue'
    import VantComponent from '@/components/VantForm/index.vue'
    import { errorHandler } from '@/utils/errorHandler.js'

    const DEFAULT_SCHEMES_NAME = window.gettext('执行所有节点')

    export default {
        name: 'TaskCreate',
        components: {
            NoData,
            VantComponent
        },
        props: { templateId: String },
        data () {
            return {
                loadingConfig: false,
                creating: false,
                show: false,
                dateTimeShow: false,
                columns: [],
                currentDate: new Date(),
                currentRef: null,
                collectedList: [],
                collected: false,
                collecting: false,
                templateData: {
                    name: '',
                    creator_name: '',
                    create_time: ''
                },
                templateConstants: {},
                schemes: [],
                scheme: DEFAULT_SCHEMES_NAME,
                i18n: {
                    loading: window.gettext('加载中'),
                    btnCreate: window.gettext('新建任务'),
                    taskName: window.gettext('任务名称'),
                    scheme: window.gettext('方案'),
                    canvasPreview: window.gettext('预览流程图'),
                    paramInfo: window.gettext('参数信息'),
                    paramInput: window.gettext('输入参数值'),
                    datetimeInput: window.gettext('请选择日期时间'),
                    taskInfo: window.gettext('任务信息'),
                    collectSuccess: window.gettext('添加收藏成功'),
                    cancelCollectSuccess: window.gettext('取消收藏成功')
                },
                taskId: 0,
                taskName: '',
                taskNameRule: {
                    required: true,
                    max: 50,
                    regex: NAME_REG
                },
                excludeTaskNodes: [], // 根据选择方案排除的节点信息
                templatePipelineTree: {}, // 模板的数据树
                variableInputRule: {
                    required: true,
                    max: 20
                }
            }
        },
        computed: {
            ...mapState({
                defaultSchemaIndex: state => state.defaultSchemaIndex
            }),

            sortedConstants () {
                const sortedTemplateConstants = {}
                const sortedConstants = Object.values(this.templateConstants).sort((a, b) => a.index - b.index)
                sortedConstants.forEach((item) => {
                    sortedTemplateConstants[item['key']] = item
                })
                return sortedTemplateConstants
            }
        },
        mounted () {
            this.creating = false
            this.loadData()
        },
        methods: {
            ...mapActions('template', [
                'getTemplate',
                'getCollectedTemplate',
                'collectTemplate',
                'deleteCollect',
                'createTask',
                'getTemplateConstants',
                'getSchemeList',
                'getScheme',
                'getPreviewTaskTree'
            ]),
            ...mapActions('component', [
                'getVariableConfig',
                'getAtomConfig'
            ]),
            async loadData () {
                this.$toast.loading({ mask: true, message: this.i18n.loading })
                Promise.all([
                    this.getTemplate(this.templateId),
                    this.getSchemeList(this.$store.state.bizId)
                ]).then(values => {
                    this.fillTemplateData(values[0])
                    this.fillSchemeData(values[1])
                    this.$toast.clear()
                }).catch(e => {
                    errorHandler(e, this)
                    this.$toast.clear()
                })
            },
            fillSchemeData (response) {
                this.schemes = response
                this.columns = [{ text: DEFAULT_SCHEMES_NAME }, ...this.schemes]
                this.scheme = this.columns[this.defaultSchemaIndex]
                this.excludeTaskNodes = this.$store.state.excludeTaskNodes
            },
            fillTemplateData (response) {
                this.templateData = response
                const pipelineTree = JSON.parse(this.templateData.pipeline_tree)
                this.templatePipelineTree = pipelineTree
                this.templateConstants = pipelineTree.constants
                this.taskName = this.getDefaultTaskName()
                this.isTemplateCollected()
                this.$store.commit('setTemplate', this.templateData)
                this.$store.commit('setPipelineTree', pipelineTree)
                this.loadAtomOrVariableConfig(this.templateConstants)
            },
            onCreateClick () {
                this.$validator.validateAll().then((result) => {
                    if (result && !this.$validator.errors.items.length) {
                        this.createTaskAndStart()
                    }
                })
            },
            async createTaskAndStart () {
                if (!this.creating) {
                    this.creating = true
                    this.$toast.loading({ mask: true, message: this.i18n.loading })
                    try {
                        const params = {
                            template_id: Number(this.templateId),
                            exclude_task_nodes_id: this.excludeTaskNodes,
                            template_source: 'project'
                        }
                        const pipelineTree = await this.getPreviewTaskTree(params)
                        Object.keys(this.templateConstants).forEach(k => {
                            if (pipelineTree.constants[k]) { // 可能存在未引用变量
                                pipelineTree.constants[k].value = this.templateConstants[k].value
                            }
                        })
                        const data = {
                            'name': this.taskName,
                            'description': '',
                            'exec_data': pipelineTree
                        }
                        const response = await this.createTask(data)
                        if (response) {
                            this.taskId = response.id
                            this.$store.commit('setTaskId', this.taskId)
                            this.$router.push({ path: '/task/canvas', query: { taskId: this.taskId } })
                        }
                    } catch (e) {
                        errorHandler(e, this)
                    } finally {
                        this.creating = false
                        this.$toast.clear()
                    }
                }
            },
            onInputDataChange (val, key, type) {
                if (type === 'datetime') {
                    this.dateTimeShow = true
                    this.currentRef = key
                } else {
                    this.templateConstants[key].value = val
                }
            },
            getDefaultTaskName () {
                return this.templateData.name + '_' + moment().format('YYYYMMDDHHmmss')
            },
            async onConfirm (value) {
                this.show = false
                let selectedSchemaIndex = 0
                if (value.id) {
                    try {
                        this.scheme = await this.getScheme(value.id)
                    } catch (e) {
                        errorHandler(e, this)
                    }
                    this.scheme.text = this.scheme.name
                    const existNodes = Object.keys(this.templatePipelineTree.activities)
                    // 排除的节点字符串
                    const includeNodesStr = this.scheme.data
                    if (includeNodesStr && includeNodesStr.length) {
                        const includeNodes = JSON.parse(includeNodesStr)
                        // 两个数组的差集，即被排除的节点
                        this.excludeTaskNodes = existNodes.filter(n => !includeNodes.includes(n))
                    }
                    selectedSchemaIndex = this.columns.findIndex(col => col.id === value.id)
                } else {
                    this.excludeTaskNodes = []
                    this.scheme = value
                }
                this.$store.commit('setExcludeTaskNodes', this.excludeTaskNodes)
                this.$store.commit('setDefaultSchemaIndex', selectedSchemaIndex)
            },
            async collect () {
                // 防止重复提交
                if (!this.collecting) {
                    this.collecting = true
                    try {
                        if (this.collected) {
                            const collected = this.collectedList.find(item => item.extra_info.id === Number(this.templateData.id))
                            const collectId = collected.id
                            await this.deleteCollect(collectId)
                            this.collected = false
                            this.$toast.success(this.i18n.cancelCollectSuccess)
                        } else {
                            const list = [{
                                extra_info: {
                                    project_id: this.templateData.project.id,
                                    template_id: this.templateData.id,
                                    name: this.templateData.name,
                                    id: this.templateData.id
                                },
                                category: 'flow'
                            }]
                            await this.collectTemplate(list)
                            this.collected = true
                            this.$toast.success(this.i18n.collectSuccess)
                        }
                        this.isTemplateCollected()
                    } catch (e) {
                        errorHandler(e, this)
                    } finally {
                        this.collecting = false
                    }
                }
            },
            async isTemplateCollected () {
                try {
                    const response = await this.getCollectedTemplate()
                    this.collectedList = response.results
                    this.collected = this.collectedList.some(template => {
                        return template.category === 'flow' && template.extra_info.id === Number(this.templateId)
                    })
                } catch (e) {
                    errorHandler(e, this)
                }
            },

            onDateTimeConfirm (value) {
                if (this.currentRef) {
                    this.$set(this.templateConstants[this.currentRef], 'value', dateFormatter(value))
                }
                this.dateTimeShow = false
            },

            onDateTimeCancel () {
                this.dateTimeShow = false
            },

            async loadAtomOrVariableConfig (constants) {
                const schemes = []
                const configMap = {}
                this.loadingConfig = true
                if (!global.$.context) {
                    const siteURL = window.SITE_URL
                    const project = this.templateData.project
                    global.$.context = {
                        project: project || undefined,
                        biz_cc_id: project ? (project.from_cmdb ? project.bk_biz_id : undefined) : undefined,
                        site_url: siteURL,
                        component: siteURL + 'api/v3/component/',
                        variable: siteURL + 'api/v3/variable/',
                        template: siteURL + 'api/v3/template/',
                        instance: siteURL + 'api/v3/taskflow/',
                        get (attr) { // 获取 $.context 对象上属性
                            return $.context[attr]
                        },
                        getBkBizId () { // 项目来自 cmdb，则获取对应的业务 id
                            if ($.context.project) {
                                return $.context.project.from_cmdb ? $.context.project.bk_biz_id : ''
                            }
                            return ''
                        },
                        getProjectId () { // 获取项目 id
                            if ($.context.project) {
                                return $.context.project.id
                            }
                            return ''
                        },
                        canSelectBiz () { // 是否可以选择业务
                            if ($.context.project) {
                                return !$.context.project.from_cmdb
                            }
                            return true
                        },
                        getConstants () { // 获取流程模板下的全局变量
                            return constants
                        }
                    }
                }
                await Promise.all(Object.keys(constants).map(async (key) => {
                    const constant = constants[key]
                    if (constant.show_type === 'show') {
                        const [configKey] = constant.source_tag.split('.')
                        const version = constant.version || 'legacy'
                        let scheme

                        if (!configMap[configKey] || !configMap[configKey][version]) {
                            try {
                                if (constant.custom_type) {
                                    scheme = await this.getVariableConfig({ customType: constant.custom_type, configKey, version })
                                } else {
                                    scheme = await this.getAtomConfig({ atomCode: configKey, version })
                                }
                                if (!configMap[configKey]) {
                                    configMap[configKey] = {
                                        [version]: scheme
                                    }
                                } else {
                                    configMap[configKey][version] = scheme
                                }
                            } catch (e) {
                                errorHandler(e, this)
                            }
                        } else {
                            scheme = configMap[configKey][version]
                        }
                        schemes.push({ key, scheme })
                    }
                }))
                schemes.forEach(item => {
                    const constant = constants[item.key]
                    this.$set(constant, 'renderConfig', item.scheme)
                })
                this.loadingConfig = false
            }

        }
    }
</script>
<style lang="scss" scoped>
    .holder-wrap {
        height: 40px;
        text-align: center;
    }
    .van-loading {
        display: inline-block;
    }
    /deep/ .bk-text-list .van-cell__title {
        min-width: 3.2rem;
    }
</style>
