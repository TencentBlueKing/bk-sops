<template>
    <div class="navbar">
        <van-nav-bar :title="title">
            <van-icon
                @click="show = true"
                name="wap-nav"
                slot="left"
                v-if="isActionSheetShow" />
        </van-nav-bar>
        <van-actionsheet
            class="navbar-list"
            v-model="show"
            position="top"
            :actions="actions"
            @select="onSelect" />
    </div>
</template>
<script>

    import { mapState } from 'vuex'

    export default {
        name: 'Navbar',
        data () {
            return {
                show: false,
                actions: [
                    {
                        name: '流程模板',
                        router: '/template'
                    },
                    {
                        name: '任务记录',
                        router: '/task/list'
                    },
                    {
                        name: '业务选择',
                        router: 'home'
                    }
                ]
            }
        },
        computed: {
            ...mapState({
                isActionSheetShow: state => state.isActionSheetShow,
                title: state => state.title
            })
        },
        methods: {
            onSelect (item) {
                // 点击选项时默认不会关闭菜单，可以手动关闭
                this.show = false
                if (item.router === 'home') {
                    this.$cookies.remove('biz_id')
                }
                this.$router.push({ path: item.router })
            }
        }
    }
</script>

<style lang="scss">
    @import '../../../static/style/app.scss';
    /*navbar*/
    .navbar{
        position: fixed;
        width: 100%;
        z-index: 1;

        .van-nav-bar{
            height: 60px;
            line-height: 60px;
            background-color: #182132;

            .van-icon{
                font-size: 24px;
                color: $white;
            }
            .van-nav-bar__title{
                color: $white;
                font-size: $font-size-16;
            }
        }
        &-list{
            top: 76px;
            color: $white;
            font-size: 14px;
            background-color: inherit;

            .van-actionsheet__item{
                background-color: #182132;
                margin: 0 10px;
                padding: 0 10px;
                font-size: 14px;
                text-align: left;

                &:first-child{
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                &:last-child{
                    border-bottom-left-radius: 4px;
                    border-bottom-right-radius: 4px;
                }
                &:first-child:after{
                    border-top: none;
                }
                &:after{
                    border-top-color: #202738;
                }
            }
        }
    }
</style>
