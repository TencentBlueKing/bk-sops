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
                <!--<van-icon slot="right-icon" name="star" class="star-icon collection" />-->
            </van-cell>
        </section>
        <!-- 任务信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">任务信息</h2>
            <!-- TODO:方案信息怎么拿？ -->
            <div class="bk-text-list">
                <van-cell title="任务名称" value="new20190313145111" />
                <van-cell @click="show = true" title="方案" value="执行所有节点" />
                <van-cell>
                    <router-link to="">预览流程图</router-link>
                </van-cell>
            </div>
        </section>
        <van-popup
            v-model="show"
            position="bottom"
            :overlay="true"
        >
            <van-picker
                show-toolbar
                :columns="columns"
                @confirm="show = false"
                @cancel="show = false"
            />
        </van-popup>
        <!-- 参数信息 -->
        <section class="bk-block">
            <h2 class="bk-text-title">参数信息</h2>
            <div class="bk-text-list">
                <van-field v-for="item in templateConstants.constants" :key="item.id"
                    label="参数01"
                    placeholder="输入参数值"
                />
            </div>
        </section>
        <!-- 按钮 -->
        <div class="btn-group">
            <van-button size="large" type="info">{{ i18n.btnCreate }}</van-button>
        </div>
    </div>
</template>

<script>
    import { mapActions } from 'vuex'

    export default {
        name: 'TaskCreate',
        data () {
            return {
                show: false,
                columns: ['执行所有节点', '方案一', '方案二', '方案三'],
                templateData: {
                    name: '',
                    creator_name: '',
                    create_time: ''
                },
                templateConstants: {},
                i18n: {
                    btnCreate: window.gettext('执行任务')
                }
            }
        },
        mounted () {
            this.loadData()
        },
        methods: {
            ...mapActions('template', [
                'getTemplate',
                'getTemplateConstants'
            ]),
            async loadData () {
                this.templateData = await this.getTemplate()
                this.templateConstants = await this.getTemplateConstants()
            }
        }
    }
</script>

<style lang="scss">
    @import '../../../static/style/app.scss';
</style>
