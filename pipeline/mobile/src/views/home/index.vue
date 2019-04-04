<template>
    <div class="index-view">
        <van-list
            v-model="loading"
            :finished="finished"
            finished-text="没有更多了"
            @load="onLoad"
        >
            <div class="panel-list">
                <van-cell v-for="item in list"
                    :to="`/template/?bizId=${item.cc_id}`"
                    :key="item.cc_id"
                    :title="item.cc_name">
                    <template slot="title">
                        <van-tag class="tag-2">{{ item.cc_id }}</van-tag>
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
                        _this.list.push(item)
                    })

                    // 加载状态结束
                    this.loading = false

                    // 数据全部加载完成
                    if (this.list.length >= bizList.length) {
                        this.finished = true
                    }
                }, 500)
            }
        }
    }
</script>

<style lang="scss">
  @import '../../../static/style/app.scss';
  .index-view {
    min-height: 100vh;
    background-color: $white;
    padding: 20px 0;
    box-sizing: border-box;

    .van-cell {
      background-color: #F0F0F0;
      height: 90px;
      margin: 0 25px 20px 25px;
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
        background-color: #ff5656 !important;
      }

      .tag-2 {
        background-color: #3A84FF !important;
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
