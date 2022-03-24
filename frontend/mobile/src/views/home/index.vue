/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="page-view">
        <van-list
            v-model="loading"
            :finished="finished"
            :finished-text="i18n.finishedText"
            :error.sync="error"
            :error-text="i18n.errorText"
            @load="onLoad">
            <div class="panel-list">
                <van-cell
                    v-for="item in projectList"
                    :key="item.id"
                    :title="item.name"
                    @click="onClickProject(item.id)">
                    <template slot="title">
                        <van-tag color="false" :class="item.tagColor">{{ item.tag }}</van-tag>
                        <span class="title">{{ item.name }}</span>
                    </template>
                </van-cell>
            </div>
        </van-list>
    </div>
</template>
<script>
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'

    const BIZ_TAG_COLORS = ['blue', 'red', 'orange', 'green', 'gray']

    export default {
        name: 'home',
        props: { title: String },

        data () {
            return {
                projectList: [],
                i18n: {
                    errorText: window.gettext('请求失败，点击重新加载'),
                    finishedText: window.gettext('没有更多了')
                },
                loading: false,
                error: false,
                finished: false,
                offset: 0,
                page: 0,
                limit: 10,
                total: 0
            }
        },
        methods: {
            ...mapActions('project', [
                'getProjectList'
            ]),

            onLoad () {
                this.loadData()
            },

            async loadData () {
                try {
                    this.page += 1
                    const response = await this.getProjectList({ offset: this.offset, limit: this.limit })
                    this.total = response.count
                    const totalPage = Math.ceil(this.total / this.limit)
                    if (this.page === totalPage) {
                        this.finished = true
                    } else {
                        this.offset = this.page * this.limit
                    }
                    this.projectList = [...this.projectList, ...response.results]
                    this.projectList.map(item => {
                        ({ tagColor: item.tagColor, tag: item.tag } = this.getTagColor(item))
                    })
                } catch (e) {
                    this.error = true
                    errorHandler(e, this)
                } finally {
                    this.loading = false
                }
            },

            getTagColor (project) {
                // tag颜色分布 1-5号色值，保存在cookie里面
                const tagColor = this.$cookies.get(project.id)
                const [tag] = project.name
                if (tagColor) {
                    return { tagColor: tagColor, tag: tag }
                } else {
                    const color = parseInt(Math.random() * 4, 10) + 1
                    const tagColor = `tag-${BIZ_TAG_COLORS[color]}`
                    this.$cookies.set(project.id, tagColor)
                    return { tagColor: tagColor, tag: tag }
                }
            },

            onClickProject (id) {
                this.$store.commit('setBizId', id)
                this.$router.push({ path: `/template/${id}` })
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '../../../static/style/var.scss';
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
            .van-cell__title{
                flex: inherit;
                display: flex;
                align-items: center;
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
                flex: 1;
            }
        }
    }
</style>
