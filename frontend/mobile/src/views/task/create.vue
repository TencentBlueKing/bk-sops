/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
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
                <template v-else>
                    <no-data />
                </template>
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
                'getTemplateList',
                'getTemplate',
                'collectTemplate',
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
                            template_id: this.templateId,
                            exclude_task_nodes_id: JSON.stringify(this.excludeTaskNodes),
                            template_source: 'business'
                        }
                        const pipelineTree = await this.getPreviewTaskTree(params)
                        Object.keys(this.templateConstants).forEach(k => {
                            pipelineTree.constants[k].value = this.templateConstants[k].value
                        })
                        const data = {
                            'name': this.taskName,
                            'description': '',
                            'exec_data': JSON.stringify(pipelineTree)
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
                    // 调用收藏是取消收藏方法
                    const params = { template_id: this.templateId, method: this.collected ? 'delete' : 'add' }
                    try {
                        const response = await this.collectTemplate(params)
                        if (response.result) {
                            this.collected = !this.collected
                            if (this.collected) {
                                this.$toast.success(this.i18n.collectSuccess)
                            } else {
                                this.$toast.success(this.i18n.cancelCollectSuccess)
                            }
                        } else {
                            errorHandler(response, this)
                        }
                    } catch (e) {
                        errorHandler(e, this)
                    } finally {
                        this.collecting = false
                    }
                }
            },
            async isTemplateCollected () {
                let templateList = this.$store.state.collectedTemplateList
                if (!templateList.length) {
                    try {
                        const response = await this.getTemplateList()
                        templateList = response.objects
                        templateList.forEach(template => {
                            if (this.templateData.id === template.id) {
                                this.templateData.is_add = template.is_add
                            }
                        })
                    } catch (e) {
                        errorHandler(e, this)
                    }
                }
                this.collected = Boolean(this.templateData.is_add)
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
                this.loadingConfig = true
                if (!global.$.context) {
                    global.$.context = {}
                }
                for (const key of Object.keys(constants)) {
                    const constant = constants[key]
                    const [configKey] = constant.source_tag.split('.')
                    if (!global.$.atoms || !global.$.atoms[configKey]) {
                        try {
                            if (constant.custom_type) {
                                await this.getVariableConfig({ customType: constant.custom_type })
                            } else {
                                await this.getAtomConfig({ atomCode: configKey })
                            }
                        } catch (e) {
                            errorHandler(e, this)
                        }
                    }
                    this.$set(constant, 'renderConfig', global.$.atoms[configKey])
                }
                this.loadingConfig = false
            }

        }
    }
</script>
