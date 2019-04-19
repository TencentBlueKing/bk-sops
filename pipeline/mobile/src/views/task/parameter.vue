<template>
    <div class="page-view">
        <!-- 输入参数 -->
        <section class="bk-block">
            <VueJsonPretty :data="parameters" class="parameter-info" />
        </section>
    </div>
</template>
<script>
    import VueJsonPretty from 'vue-json-pretty'
    import { mapActions } from 'vuex'

    export default {
        name: 'task_node_parameter',
        components: {
            VueJsonPretty
        },
        // props: { taskId: String, parameters: Object },
        data () {
            return {
                parameters: {}
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
                this.parameters = JSON.parse(this.$route.params.parameters)
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
        left: 0;
        right: 0;
    }
</style>
