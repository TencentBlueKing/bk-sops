<template>
    <div class="page-view">
        <van-list
            v-model="loading"
            :finished="finished"
            :finished-text="i18n.finished_text"
            @load="onLoad">
            <div class="panel-list">
                <van-cell
                    v-for="item in businessList"
                    :key="item.cc_id"
                    :title="item.cc_name"
                    @click="onClickBusiness(item.cc_id)">
                    <template slot="title">
                        <van-tag color="false" :class="item.tagColor">{{ item.tag }}</van-tag>
                        <span class="title">{{ item.cc_name }}</span>
                    </template>
                </van-cell>
            </div>
        </van-list>
    </div>
</template>
<script>
    import { mapActions } from 'vuex'

    const BIZ_TAG_COLORS = ['blue', 'red', 'orange', 'green', 'gray']

    export default {
        name: 'home',
        props: { title: String },

        data () {
            return {
                businessList: [],
                i18n: {
                    finished_text: window.gettext('没有更多了')
                },
                loading: false,
                finished: false,
                offset: 0,
                limit: 10,
                total: 0
            }
        },
        methods: {
            ...mapActions('business', [
                'getBusinessList'
            ]),

            onLoad () {
                this.loadData()
            },

            async loadData () {
                const response = await this.getBusinessList({ offset: this.offset, limit: this.limit })
                this.total = response.meta.total_count
                const totalPage = Math.ceil(this.total / this.limit)
                if (this.offset + 1 >= totalPage) {
                    this.finished = true
                } else {
                    this.offset = this.offset + 1
                }
                this.loading = false
                this.businessList = [...this.businessList, ...response.objects]
                this.businessList.map(item => {
                    ({ tagColor: item.tagColor, tag: item.tag } = this.getTagColor(item))
                })
            },

            getTagColor (biz) {
                // tag颜色分布 1-5号色值，保存在cookie里面
                const tagColor = this.$cookies.get(biz.cc_id)
                const [tag] = biz.cc_name
                if (tagColor) {
                    return { tagColor: tagColor, tag: tag }
                } else {
                    const color = parseInt(Math.random() * 4, 10) + 1
                    const tagColor = `tag-${BIZ_TAG_COLORS[color]}`
                    this.$cookies.set(biz.cc_id, tagColor)
                    return { tagColor: tagColor, tag: tag }
                }
            },

            onClickBusiness (bizId) {
                this.$store.commit('setBizId', bizId)
                this.$router.push({ path: `/template/${bizId}` })
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
            &:after{
                border-bottom: none;
            }
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
                vertical-align: middle;
            }
            .tag-blue {
                background-color: #3A84FF;
            }
            .tag-red {
                background-color: #EA3636;
            }
            .tag-orange {
                background-color: #FF9C01;
            }
            .tag-green {
                background-color: #2DCB56;
            }
            .tag-gray {
                background-color: #C4C6CC;
            }
            .title {
                font-size: $fs-16;
                font-weight: bold;
                margin-left: 10px;
                color: $black;
                vertical-align: middle;
            }
        }
    }
</style>
