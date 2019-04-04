<template>
    <div>
        <div class="page-list">
            <!-- 搜索 -->
            <van-search :placeholder="i18n.placeholder" v-model="value" class="process-search" />
            <!-- 收藏 -->
            <section class="bk-block">
                <h2 class="bk-block-title">{{ i18n.collect }}</h2>
                <van-cell clickable v-for="item in collectTemplateList"
                    :to="`/template/task_create?templateId=${item.id}`" :key="item.id">
                    <template slot="title">
                        <div class="bk-text">{{ item.name }}</div>
                        <div class="bk-name">{{ item.creator_name }}</div>
                        <div class="bk-time">{{ item.create_time }}</div>
                    </template>
                    <van-icon slot="right-icon" name="star" class="star-icon collection" />
                </van-cell>
            </section>
            <!-- 开区 -->
            <section class="bk-block">
                <h2 class="bk-block-title">{{ templateList[0].business.cc_name }}</h2>
                <van-cell clickable :to="`/template/task_create?templateId=${item.cc_id}`"
                    v-for="item in templateList" :key="item.id">
                    <template slot="title">
                        <div class="bk-text">{{ item.name }}</div>
                        <div class="bk-name">{{ item.creator_name }}</div>
                        <div class="bk-time">{{ item.create_time }}</div>
                    </template>
                </van-cell>
            </section>
        </div>
        <!-- 标签栏 -->
        <van-tabbar v-model="active" class="bk-tabbar">
            <van-tabbar-item>
                <span>流程</span>
                <img
                    slot="icon"
                    slot-scope="props"
                    :src="props.active ? icon_process.active : icon_process.normal"
                >
            </van-tabbar-item>
            <van-tabbar-item>
                <span>任务</span>
                <img
                    slot="icon"
                    slot-scope="props"
                    :src="props.active ? icon_task.active : icon_task.normal"
                >
            </van-tabbar-item>
        </van-tabbar>
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
                i18n: {
                    collect: window.gettext('收藏'),
                    finished_text: window.gettext('没有更多了'),
                    placeholder: window.gettext('搜索流程名称')
                },
                active: 0,
                value: '',
                icon_process: {
                    normal: '/static/images/icon-process-normal.png',
                    active: '/static/images/icon-process-active.png'
                },
                icon_task: {
                    normal: '/static/images/icon-task-normal.png',
                    active: '/static/images/icon-task-active.png'
                }
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
            }
        }
    }
</script>

<style lang="scss">
  @import '../../../static/style/app.scss';
  .page-list{
    background: $white;
    min-height: 100vh;
    padding-bottom: 50px;
    -webkit-box-sizing: border-box;
    box-sizing: border-box;
  }
  /*search*/
  .process-search{
    background-color: #F2F2F2!important;
    padding: 8px 25px;

    .van-search__content{
      background-color: $white;
      -webkit-border-radius: 10px;
      -moz-border-radius: 10px;
      border-radius: 10px;

      .van-cell{
        padding: 6px 10px 6px 0;
      }
    }
  }
</style>
