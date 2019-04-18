<template>
    <div class="page-view">
        <div class="task-status info">
            执行中
        </div>
        <div class="task-status warning">
            暂停
        </div>
        <div class="task-status danger">
            撤销
        </div>
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

<style lang="scss">
    @import '../../../static/style/app.scss';
    .task-status{
        border-bottom-style: solid;
        border-bottom-width: 1px;
        padding: 10px;
        text-align: center;
        font-size: $fs-14;
    }
    .task-status.info{
        background: #CFDFFB;
        border-bottom-color: #C0D4F8;
        color: $blue;
    }
    .task-status.warning{
        background: #FFE8C3;
        border-bottom-color: #E6CFAA;
        color: #D78300;
    }
    .task-status.danger{
        background: #F2D0D3;
        border-bottom-color: #EFB9BE;
        color: #EA3636;
    }
    .van-tabbar{
        background-color: $background-color;

        .van-tabbar-item__icon{
            font-size: 22px;
            margin-bottom: 0;

            .icon-pause,.icon-pause{
                color: $blue;
            }
            .icon-revoke{
                color: #EA3636;
            }
            .icon-file{
                color: #4E4E4E;
            }
            .disabled{
                opacity: 0.4;
            }
        }

        &:after{
            border-color: #E5E5E5;
        }
    }
</style>
