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
                    v-validate="taskNameRule"
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
        <van-popup
            v-model="show"
            position="bottom"
            :overlay="true">
            <van-picker
                show-toolbar
                :columns="columns"
                @confirm="onConfirm"
                @cancel="show = false" />
        </van-popup>

        <van-popup
            v-model="datetimePickerShow"
            position="bottom"
            :overlay="true">
            <van-datetime-picker
                type="datetime"
                show-toolbar
                v-model="currentDate"
                @confirm="onDatetimePickerConfirm"
                @cancel="onDatetimePickerCancel" />
        </van-popup>
        <!-- 参数信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">{{ i18n.paramInfo }}</h2>
            <div class="bk-text-list">
                <template v-if="Object.keys(templateConstants).length">
                    <template v-for="item in templateConstants">
                        <van-field
                            v-if="item.custom_type === 'input'"
                            :key="item.id"
                            :label="item.name"
                            :placeholder="i18n.paramInput"
                            v-validate="variableInputRule"
                            v-model="item.value"
                            :value="item.value" />
                        <van-field
                            v-else-if="item.custom_type === 'int'"
                            type="number"
                            :key="item.id"
                            :label="item.name"
                            :placeholder="i18n.paramInput"
                            v-model="item.value"
                            :value="item.value" />
                        <van-cell
                            v-else-if="item.custom_type === 'datetime'"
                            :placeholder="i18n.datetimeInput"
                            :key="item.id"
                            :title="item.name"
                            :value="item.value"
                            @click="datetimePickerShow = true">
                            <template v-if="datetimeVariable">
                                {{ datetimeVariable }}
                            </template>
                            <template v-else>
                                {{ item.value }}
                            </template>
                        </van-cell>
                        <van-field
                            v-if="item.custom_type === 'textarea'"
                            v-model="item.value"
                            type="textarea"
                            :placeholder="i18n.paramInput"
                            v-validate="variableInputRule"
                            rows="1"
                            autosize
                            :key="item.id"
                            :label="item.name"
                            :value="item.value" />
                    </template>
                </template>
                <template v-else>
                    <van-cell title="" :value="i18n.noData" />
                </template>
            </div>
        </section>
        <div class="btn-group">
            <van-button
                v-if="creating"
                loading
                disabled
                :loading-text="i18n.btnCreating"
                size="large"
                type="info" />
            <van-button
                v-else
                size="large"
                type="info"
                @click="createTaskAndStart">{{ i18n.btnCreate }}</van-button>
        </div>
    </div>
</template>

<script>
    import moment from 'moment'
    import { mapActions } from 'vuex'
    import { dateFormatter } from '@/common/util.js'

    const NAME_REG = /^[A-Za-z0-9\_\-\[\]\【\】\(\)\（\）\u4e00-\u9fa5]+$/
    const DEFAULT_SCHEMES_NAME = window.gettext('执行所有节点')

    export default {
        name: 'TaskCreate',
        props: { templateId: String },
        data () {
            return {
                creating: false,
                show: false,
                datetimeVariable: '',
                datetimePickerShow: false,
                numberKeyboardShow: false,
                columns: [],
                currentDate: new Date(),
                collected: false,
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
                    btnCreate: window.gettext('执行任务'),
                    btnCreating: window.gettext('执行任务...'),
                    taskName: window.gettext('任务名称'),
                    scheme: window.gettext('方案'),
                    canvasPreview: window.gettext('预览流程图'),
                    paramInfo: window.gettext('参数信息'),
                    paramInput: window.gettext('输入参数值'),
                    datetimeInput: window.gettext('请选择日期时间'),
                    taskInfo: window.gettext('任务信息'),
                    noData: window.gettext('暂无数据')
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
        mounted () {
            this.creating = false
            this.loadData()
        },
        methods: {
            ...mapActions('template', [
                'getTemplate',
                'collectTemplate',
                'createTask',
                'getTemplateConstants',
                'getSchemes',
                'getScheme',
                'getPreviewTaskTree'
            ]),
            async loadData () {
                this.$toast.loading({ mask: true, message: this.i18n.loading })
                this.templateData = await this.getTemplate(this.templateId)
                const pipelineTree = JSON.parse(this.templateData.pipeline_tree)
                this.templateConstants = pipelineTree.constants
                this.schemes = await this.getSchemes(this.$store.state.bizId)
                this.taskName = this.getDefaultTaskName()
                this.collected = this.templateData.is_favorite
                this.columns = [{ text: DEFAULT_SCHEMES_NAME }, ...this.schemes]
                this.$store.commit('setTemplate', this.templateData)
                this.templatePipelineTree = JSON.parse(this.templateData.pipeline_tree)
                this.$toast.clear()
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
                        pipelineTree.constants = this.templateConstants
                        const data = {
                            'name': this.taskName,
                            'description': '',
                            'exec_data': JSON.stringify(pipelineTree)
                        }
                        const response = await this.createTask(data)
                        if (response) {
                            this.taskId = response.id
                            this.$store.commit('setTaskId', this.taskId)
                        }
                        this.$router.push({ path: '/task/canvas', query: { 'executeTask': 'true', taskId: this.taskId } })
                    } catch (e) {
                        console.error(e)
                    } finally {
                        this.creating = false
                        this.$toast.clear()
                    }
                }
            },
            getDefaultTaskName () {
                return this.templateData.name + '_' + moment().format('YYYYMMDDHHmmss')
            },
            async onConfirm (value) {
                this.show = false
                if (value.id) {
                    this.scheme = await this.getScheme(value.id)
                    this.scheme.text = this.scheme.name
                    const existNodes = Object.keys(this.templatePipelineTree.activities)
                    // 排除的节点字符串
                    const includeNodesStr = this.scheme.data
                    if (includeNodesStr && includeNodesStr.length) {
                        const includeNodes = JSON.parse(includeNodesStr)
                        // 两个数组的差集，即被排除的节点
                        this.excludeTaskNodes = includeNodes.concat(existNodes).filter(v => includeNodes.includes(v) ^ existNodes.includes(v))
                        this.$store.commit('setExcludeTaskNodes', this.excludeTaskNodes)
                    }
                } else {
                    this.scheme = value
                }
            },
            onDatetimePickerConfirm (value) {
                this.datetimePickerShow = false
                this.datetimeVariable = dateFormatter(value)
            },
            onDatetimePickerCancel () {
                this.datetimePickerShow = false
            },
            async collect () {
                // 调用收藏是取消收藏方法
                this.collected = await this.collectTemplate(this.collected)
            }
        }
    }
</script>

<style lang="scss">
    @import '../../../static/style/app.scss';
</style>
