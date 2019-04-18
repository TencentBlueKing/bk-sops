<template>
    <div class="page-view">
        <!-- 输入参数 -->
        <section class="bk-block">
            <div class="parameter-info">
                { "activities":{ "error_ignorable":false, "component":{ "code":"bk_notify", "data":{ "bk_notify_type":{ "hook":false] }, { "activities":{ "error_ignorable":false, "component":{ "code":"bk_notify", "data":{ "bk_notify_type":{ "hook":false ] },
                { "activities":{ "error_ignorable":false, "component":{ "code":"bk_notify", "data":{ "bk_notify_type":{ "hook":false] }, { "activities":{ "error_ignorable":false, "component":{ "code":"bk_notify", "data":{ "bk_notify_type":{ "hook":false ] },
            </div>
        </section>
    </div>
</template>
<script>
    import { mapActions } from 'vuex'

    export default {
        name: 'TaskParameter',
        data () {
            return {
                task: {}
            }
        },
        mounted () {
            this.loadData()
        },
        methods: {
            ...mapActions('task', [
                'getTask'
            ]),

            async loadData () {
                this.task = await this.getTask()
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '../../../static/style/app.scss';
    .parameter-info{
        background: #313238;
        min-height: 100px;
        color: $white;
        font-size: $fs-14;
        padding: 15px 25px;
        position: absolute;
        top: 0;
        bottom: 0;
    }
</style>
