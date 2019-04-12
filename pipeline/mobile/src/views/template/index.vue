<template>
    <div class="page-view">
        <!-- 搜索 -->
        <van-search
            :placeholder="i18n.placeholder"
            v-model="value"
            class="bk-search"
            @search="search()">
        </van-search>
        <!-- 收藏 -->
        <section class="bk-block">
            <h2 class="bk-block-title">{{ i18n.collect }}</h2>
            <van-cell
                clickable
                v-for="item in collectTemplateList"
                :to="`/task/create?templateId=${item.id}`"
                :key="item.id">
                <template slot="title">
                    <div class="bk-text">{{ item.name }}</div>
                    <div class="bk-name">{{ item.creator_name }}</div>
                    <div class="bk-time">{{ item.create_time }}</div>
                </template>
                <van-icon class="star-icon collection" slot="right-icon" name="star" />
            </van-cell>
        </section>
        <!-- 开区 -->
        <section class="bk-block">
            <h2 class="bk-block-title">{{ business.cc_name }}</h2>
            <van-cell
                clickable
                :to="`/task/create?templateId=${item.id}`"
                v-for="item in templateList" :key="item.id">
                <template slot="title">
                    <div class="bk-text">{{ item.name }}</div>
                    <div class="bk-name">{{ item.creator_name }}</div>
                    <div class="bk-time">{{ item.create_time }}</div>
                </template>
            </van-cell>
        </section>
    </div>
</template>

<script>
    import { mapActions } from 'vuex'

    export default {
        name: 'TemplateList',
        data () {
            return {
                collectTemplateList: [],
                templateList: [],
                originalTemplateList: [],
                business: {
                    cc_name: ''
                },
                i18n: {
                    collect: window.gettext('收藏'),
                    finished_text: window.gettext('没有更多了'),
                    placeholder: window.gettext('搜索流程名称')
                },
                value: ''
            }
        },
        mounted () {
            this.loadData()
        },
        methods: {
            ...mapActions('templateList', [
                'getTemplateList',
                'getCollectTemplateList'
            ]),

            async loadData () {
                this.collectTemplateList = await this.getCollectTemplateList()
                this.templateList = await this.getTemplateList()
                this.originalTemplateList = this.templateList
                if (this.templateList.length > 0) {
                    this.business = this.templateList[0]['business']
                }
            },

            search () {
                const arr = []
                for (let i = 0; i < this.originalTemplateList.length; i++) {
                    if (this.originalTemplateList[i].name.includes(this.value)) {
                        arr.push(this.originalTemplateList[i])
                    }
                }
                this.templateList = arr
            }
        }
    }
</script>

<style lang="scss">
  @import '../../../static/style/app.scss';
</style>
