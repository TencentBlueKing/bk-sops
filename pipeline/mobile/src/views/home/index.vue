<template>
    <div class="page-view">
        <van-list
            v-model="loading"
            :finished="finished"
            finished-text="没有更多了"
            @load="onLoad">
            <div class="panel-list">
                <van-cell
                    v-for="item in list"
                    :to="`/template/?bizId=${item.cc_id}`"
                    :key="item.cc_id"
                    :title="item.cc_name">
                    <template slot="title">
                        <van-tag :class="item.tagColor">{{ item.tag }}</van-tag>
                        <span class="title">{{ item.cc_name }}</span>
                    </template>
                </van-cell>
            </div>
        </van-list>
    </div>
</template>
<script>
    import { getBusinessList } from '@/store/modules/businessList'

    export default {
        name: 'home',
        props: { title: String },

        data () {
            return {
                list: [],
                loading: false,
                finished: false
            }
        },

        methods: {
            onLoad () {
                // 异步更新数据
                setTimeout(() => {
                    const bizList = getBusinessList()['objects']
                    const _this = this
                    bizList.forEach(item => {
                        ({ tagColor: item.tagColor, tag: item.tag } = this.getTagColor(item))
                        _this.list.push(item)
                    })

                    // 加载状态结束
                    this.loading = false

                    // 数据全部加载完成
                    if (this.list.length >= bizList.length) {
                        this.finished = true
                    }
                }, 500)
            },

            getTagColor (biz) {
                // tag颜色分布 1-5号色值，保存在cookie里面
                const tagColor = this.$cookies.get(biz.cc_id)
                const [tag] = biz.cc_name
                if (tagColor) {
                    return { tagColor: tagColor, tag: tag }
                } else {
                    const color = parseInt(Math.random() * 5, 10) + 1
                    const tagColor = `tag-${color}`
                    this.$cookies.set(biz.cc_id, tagColor)
                    return { tagColor: tagColor, tag: tag }
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
  @import '../../../static/style/app.scss';
  .page-view {
    .van-cell {
      background-color: $white;
      height: 90px;
      margin: 20px 25px;
      width: auto;
      border-radius: 10px;
      padding: 15px;
      box-sizing: border-box;

      .van-tag {
        width: 60px;
        height: 60px;
        line-height: 60px;
        border-radius: 4px;
        text-align: center;
        display: inline-block;
        padding: 0;
        font-size: 28px;
        color: $white;
      }

      .tag-1 {
        background-color: #3A84FF !important;
      }

      .tag-2 {
        background-color: #EA3636 !important;
      }

      .tag-3 {
        background-color: #FF9C01 !important;
      }

      .tag-4 {
        background-color: #2DCB56 !important;
      }

      .tag-5 {
        background-color: #C4C6CC !important;
      }

      .title {
        font-size: 16px;
        font-weight: bold;
        margin-left: 10px;
        color: $black;
      }
    }
  }
</style>
