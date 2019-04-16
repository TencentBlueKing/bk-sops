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
                <van-icon slot="right-icon" name="star" class="star-icon collection" />
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
        <!-- 参数信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">参数信息</h2>
            <div class="bk-text-list">
                <van-field
                    v-for="item in templateConstants"
                    :key="item.id"
                    :label="item.name"
                    placeholder="输入参数值"
                    :value="item.value" />
            </div>
        </section>
        <!-- 按钮 -->
        <div class="btn-group">
            <van-button size="large" type="info">{{ i18n.btnCreate }}</van-button>
        </div>
    </div>
</template>

<script>
    import moment from 'moment'
    import { mapActions } from 'vuex'

    const NAME_REG = /^[A-Za-z0-9\_\-\[\]\【\】\(\)\（\）\u4e00-\u9fa5]+$/

    export default {
        name: 'TaskCreate',
        data () {
            return {
                show: false,
                columns: [],
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
                taskName: '',
                taskNameRule: {
                    required: true,
                    max: 50,
                    regex: NAME_REG
                }
            }
        },
        mounted () {
            this.loadData()
        },
        methods: {
            ...mapActions('template', [
                'getTemplate',
                'getTemplateConstants',
                'getSchemes'
            ]),
            async loadData () {
                this.templateData = await this.getTemplate()
                this.templateConstants = await this.getTemplateConstants()
                this.schemes = await this.getSchemes()
                this.taskName = this.getDefaultTaskName()
                this.columns = [{ text: '执行所有节点' }, ...this.schemes]
            },
            getDefaultTaskName () {
                return this.templateData.name + '_' + moment().format('YYYYMMDDHHmmss')
            },
            onConfirm (value) {
                this.show = false
                this.scheme = value
            }
        }
    }
</script>

<style lang="scss">
    @import '../../../static/style/app.scss';
</style>
