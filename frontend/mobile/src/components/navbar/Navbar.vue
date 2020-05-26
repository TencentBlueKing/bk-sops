/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
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
                        router: '/template/'
                    },
                    {
                        name: '任务记录',
                        router: '/task/list'
                    },
                    {
                        name: '业务选择',
                        router: '/'
                    }
                ]
            }
        },
        computed: {
            ...mapState({
                bizId: state => state.bizId,
                isActionSheetShow: state => state.isActionSheetShow,
                title: state => state.title
            })
        },
        methods: {
            onSelect (item) {
                // 点击选项时默认不会关闭菜单，可以手动关闭
                this.show = false
                this.$cookies.set('biz_selected', true)
                if (item.router === '/template/') {
                    this.$router.push({ path: item.router + this.bizId, query: { 'biz_selected': '1' } })
                } else {
                    this.$router.push({ path: item.router, query: { 'biz_selected': '1' } })
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '../../../static/style/var.scss';
    /*navbar*/
    .navbar{
        width: 100%;
        position: fixed;
        top:0;
        z-index: 2;

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
                font-size: $fs-16;
            }
            &:after{
                border-bottom: none;
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
                font-size: $fs-14;
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
                    border-top-color: #262f44;
                }
            }
        }
        .van-popup-slide-top-enter,
        .van-popup-slide-top-leave-active {
            transform: translate3d(-50%, -20%, 0);
        }
    }
</style>
