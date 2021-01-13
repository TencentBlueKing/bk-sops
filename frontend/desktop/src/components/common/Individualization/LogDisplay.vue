/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="log-display" :style="containerStyle">
        <bk-virtual-scroll
            ref="logVirtualScroll"
            class="log-virtual-scroll"
            :show-index="showIndex"
            :show-min-map="showMinMap"
            :item-height="itemHeight">
            <template slot-scope="item">
                <span class="item-txt">{{item.data}}</span>
            </template>
        </bk-virtual-scroll>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    export default {
        name: 'IpLogContent',
        props: {
            /**
             * 显示索引
             */
            showIndex: {
                type: Boolean,
                default: true
            },
            /**
             * 显示小地图
             */
            showMinMap: {
                type: Boolean,
                default: true
            },
            /**
             * 单行高度
             */
            itemHeight: {
                type: Number,
                default: 16
            },
            /**
             * 显示日志为字符串，\n 换行
             */
            logContent: {
                type: String,
                default: ''
            },
            /**
             * 容器高度
             */
            height: {
                type: Number,
                default: 360
            },
            /**
             * 单行字数最大值
             */
            maximum: {
                type: Number,
                default: 90
            }
        },
        data () {
            return {
                containerStyle: {
                    height: this.height + 'px'
                }
            }
        },
        watch: {
            logContent () {
                this.clearData()
                this.initData()
            }
        },
        mounted () {
            this.initData()
        },
        methods: {
            initData () {
                const list = this.getDisplayList()
                this.$refs.logVirtualScroll.setListData(list)
                this.$refs.logVirtualScroll.getListData()
            },
            getDisplayList () {
                const max = this.maximum
                const list = this.logContent.split('\n')
                const cutList = []
                for (let i = 0; i <= list.length; i++) {
                    const item = list[i]
                    if (typeof item !== 'string') {
                        continue
                    }
                    let s = item
                    while (s.length > max) { // 单条大于 max 切成多段
                        cutList.push(s.slice(0, max))
                        s = s.slice(max)
                    }
                    if (s.length) {
                        cutList.push(s)
                    }
                }
                return cutList
            },
            clearData () {
                this.$refs.logVirtualScroll.setListData([])
                this.$refs.logVirtualScroll.getListData()
            }
        }
    }
</script>
<style lang="scss" scoped>
.log-display {
    width: 100%;
    overflow: hidden;
    .log-virtual-scroll {
        width: 100%;
        height: 100%;
        line-height: 16px;
        color: #ffffff;
        font-size: 12px;
        font-weight: normal;
        letter-spacing: 0px;
        white-space: nowrap;
        background: #1c2026;
        cursor: text;
        .item-txt {
            padding: 0 20px;
        }
    }
}
</style>
