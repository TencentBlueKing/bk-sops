<template>
    <div class="page-view">
        <div class="task-status danger">
            失败
        </div>
        <!--演示试用 start-->
        <div class="canvas-demo">
            <div class="container">
                <div class="box">演示</div>
                <div class="tips-bar">
                    <van-button type="default" class="">执行详情</van-button>
                    <van-button type="default" class="">重试</van-button>
                    <van-button type="default" class="">跳过</van-button>
                </div>
            </div>
        </div>
        <!--演示试用 end-->
        <van-tabbar>
            <van-tabbar-item>
                <van-icon slot="icon" class-prefix="icon" name="pause" class="disabled" disabled />
            </van-tabbar-item>
            <van-tabbar-item>
                <van-icon slot="icon" class-prefix="icon" name="revoke" />
            </van-tabbar-item>
            <van-tabbar-item>
                <van-icon slot="icon" class-prefix="icon" name="file" />
            </van-tabbar-item>
        </van-tabbar>
    </div>
</template>
<script>
    import { mapActions } from 'vuex'

    export default {
        name: '',
        data () {
            return {
                templateData: {
                    name: '',
                    creator_name: '',
                    create_time: ''
                },
                templateConstants: {}
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

<style lang="scss" scoped>
    @import '../../../static/style/app.scss';
    /*以下为演示试用可删除*/
    .canvas-demo{
        align-items: center;
        display: flex;
        justify-content: center;
        height: calc(100% - 90px);
        .container{
            width: 100%;
            text-align: center;
            position: relative;
            .box{
                width: 120px;
                height: 60px;
                line-height: 60px;
                border:1px solid #EA3636;
                background: #fff;
                margin: auto;
                font-size: 14px;
            }
            .tips-bar{
                position: absolute;
                width: 100%;
                top: -60px;
            }
        }
    }
</style>
