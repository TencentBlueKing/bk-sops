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
                    @click="collect"
                    name="star"
                    class="star-icon collection"
                    v-if="collected" />
                <van-icon
                    slot="right-icon"
                    @click="collect"
                    name="star"
                    class="star-icon"
                    v-else />
            </van-cell>
        </section>
        <!-- 任务信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">任务信息</h2>
            <div class="bk-text-list">
                <van-field
                    label="任务名称"
                    v-validate="taskNameRule"
                    v-model="taskName" />
                <van-cell
                    @click="show = true"
                    title="方案"
                    :value="scheme" />
                <van-cell>
                    <router-link to="">预览流程图</router-link>
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
                show-toolbar
                v-model="currentDate"
                @confirm="onDatetimePickerConfirm"
                @cancel="onDatetimePickerCancel"
                type="datetime" />
        </van-popup>
        <!-- 参数信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">参数信息</h2>
            <div class="bk-text-list">
                <template v-for="item in templateConstants">
                    <van-field
                        v-if="item.custom_type === 'input' || item.custom_type === 'int'"
                        :key="item.id"
                        :label="item.name"
                        placeholder="输入参数值"
                        v-validate="variableInputRule"
                        v-model="item.value"
                        :value="item.value" />
                    <van-cell
                        v-else-if="item.custom_type === 'datetime'"
                        :key="item.id"
                        :title="item.name"
                        placeholder="请选择日期时间"
                        @click="datetimePickerShow = true"
                        :value="item.value">
                        <template v-if="datetimeVariable">
                            {{ datetimeVariable }}
                        </template>
                        <template v-else>
                            {{ item.value }}
                        </template>
                    </van-cell>
                    <van-field
                        v-if="item.custom_type === 'textarea'"
                        :key="item.id"
                        :label="item.name"
                        type="textarea"
                        placeholder="输入参数值"
                        v-validate="variableInputRule"
                        rows="1"
                        autosize
                        v-model="item.value"
                        :value="item.value" />
                </template>
            </div>
        </section>
        <!-- 按钮 -->
        <div class="btn-group">
            <van-button size="large" type="info" :to="`/task/canvas?taskId=${taskId}`">{{ i18n.btnCreate }}</van-button>
        </div>
    </div>
</template>

<script>
    import moment from 'moment'
    import { mapActions } from 'vuex'
    import { dateFormatter } from '@/common/util.js'

    const NAME_REG = /^[A-Za-z0-9\_\-\[\]\【\】\(\)\（\）\u4e00-\u9fa5]+$/
    const INT_INPUT_REG = /^[0-9]+$/

    export default {
        name: 'TaskCreate',
        data () {
            return {
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
                scheme: '执行所有节点',
                i18n: {
                    btnCreate: window.gettext('执行任务')
                },
                taskId: 0,
                taskName: '',
                taskNameRule: {
                    required: true,
                    max: 50,
                    regex: NAME_REG
                },
                variableInputRule: {
                    required: true,
                    max: 20,
                    regex: INT_INPUT_REG
                }
            }
        },
        mounted () {
            this.loadData()
        },
        methods: {
            ...mapActions('template', [
                'getTemplate',
                'collectTemplate',
                'getTemplateConstants',
                'getSchemes'
            ]),
            async loadData () {
                this.templateData = await this.getTemplate()
                this.templateConstants = await this.getTemplateConstants()
                this.schemes = await this.getSchemes()
                this.taskName = this.getDefaultTaskName()
                this.collected = this.templateData.is_favorite
                this.columns = [{ text: '执行所有节点' }, ...this.schemes]
            },
            async createTask () {
                this.taskId = await this.createTask()
            },
            getDefaultTaskName () {
                return this.templateData.name + '_' + moment().format('YYYYMMDDHHmmss')
            },
            onConfirm (value) {
                this.show = false
                this.scheme = value
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
                this.collected = await this.collectTemplate(this.templateData.is_favorite)
            }
        }
    }
</script>

<style lang="scss">
    @import '../../../static/style/app.scss';
</style>
