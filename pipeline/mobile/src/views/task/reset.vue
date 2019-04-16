<template>
    <div class="page-view">
        <!-- 任务信息 -->
        <section class="bk-block">
            <div class="bk-text-list">
                <van-field label="参数01" placeholder="输入参数值" />
                <van-field label="参数02" placeholder="输入参数值" />
            </div>
        </section>
        <div class="btn-group">
            <van-button size="large" type="default">取消</van-button>
            <van-button size="large" type="info">确定</van-button>
        </div>
        <van-button @click="show11 = true" type="info">99999</van-button>
        <van-popup
            v-model="show11"
            position="bottom"
            :overlay="true">
            <van-picker
                show-toolbar
                :columns="columns"
                @confirm="show11 = false"
                @cancel="show11 = false" />
        </van-popup>
    </div>
</template>
<script>
    import { mapActions } from 'vuex'

    export default {
        name: 'TaskReset',
        data () {
            return {
                show11: false,
                columns: ['杭州', '宁波', '温州', '嘉兴', '湖州'],
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
