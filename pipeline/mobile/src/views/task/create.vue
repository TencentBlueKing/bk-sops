<template>
    <div>
        <!-- 容器 -->
        <div class="task-container">
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
                    <van-cell title="方案" value="方案一" />
                    <van-cell>
                        <router-link to="">预览流程图</router-link>
                    </van-cell>
                </div>
            </section>
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
        </div>
        <!-- 按钮 -->
        <div class="task-action">
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
    /*container*/
    .task-container {
        position: absolute;
        bottom: 90px;
        top: 0;
        width: 100%;
        overflow-y: auto;
        -webkit-box-sizing: border-box;
        box-sizing: border-box;
    }

    /*button*/
    .task-action {
        position: fixed;
        background-color: #f7f7f7;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 20px;
        z-index: 1;

        .van-button {
            border-radius: 4px;
            background-color: $blue;
            border-color: $blue;
        }
    }
</style>
