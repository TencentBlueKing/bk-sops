/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="page-view">
        <!-- 搜索 -->
        <van-search
            background="false"
            :placeholder="i18n.placeholder"
            v-model="value"
            class="bk-search"
            @change="search()"
            @clear="search()"
            @search="search()">
        </van-search>
        <!-- 收藏 -->
        <section class="bk-block" v-if="collectTemplateList.length > 0">
            <h2 class="bk-block-title">{{ i18n.collect }}</h2>
            <van-cell
                clickable
                v-for="item in collectTemplateList"
                :key="item.id"
                @click="onClickTemplate(item.id)">
                <template slot="title">
                    <div class="bk-text">{{ item.name }}</div>
                    <div class="bk-name">{{ item.creator_name }}</div>
                    <div class="bk-time">{{ item.create_time }}</div>
                </template>
                <van-icon class="star-icon collection" slot="right-icon" name="star" />
            </van-cell>
        </section>
        <!-- 模板列表 -->
        <section class="bk-block">
            <h2 class="bk-block-title" v-if="templateList.length > 0">{{ business.cc_name }}</h2>
            <van-list
                v-model="loading"
                :finished="finished"
                :finished-text="i18n.finishedText"
                :error.sync="error"
                :error-text="i18n.errorText"
                @load="loadData">
                <van-cell
                    v-for="item in templateList"
                    :key="item.id"
                    @click="onClickTemplate(item.id)">
                    <template slot="title">
                        <div class="bk-text">{{ item.name }}</div>
                        <div class="bk-name">{{ item.creator_name }}</div>
                        <div class="bk-time">{{ item.create_time }}</div>
                    </template>
                </van-cell>
            </van-list>
        </section>
    </div>
</template>

<script>
    import { errorHandler } from '@/utils/errorHandler.js'
    import { mapActions } from 'vuex'

    export default {
        name: 'TemplateList',
        props: { bizId: String },
        data () {
            return {
                collectTemplateList: [],
                templateList: [],
                originalCollectTemplateList: [],
                originalTemplateList: [],
                business: {
                    cc_name: ''
                },
                i18n: {
                    collect: window.gettext('收藏'),
                    finishedText: window.gettext('没有更多了'),
                    errorText: window.gettext('请求失败，点击重新加载'),
                    placeholder: window.gettext('搜索流程名称')
                },
                loading: false,
                finished: false,
                error: false,
                offset: 0,
                currPage: 1,
                limit: 10,
                total: 0,
                value: ''
            }
        },
        methods: {
            ...mapActions('template', [
                'getTemplateList'
            ]),

            async loadData () {
                try {
                    const response = await this.getTemplateList({ offset: this.offset, limit: this.limit })
                    this.total = response.meta.total_count
                    const totalPage = Math.ceil(this.total / this.limit)
                    if (this.currPage >= totalPage) {
                        this.finished = true
                    } else {
                        this.offset = this.currPage * this.limit
                        this.currPage += 1
                    }
                    this.templateList = [...this.templateList, ...response.objects]
                    this.originalTemplateList = this.templateList
                    if (this.templateList.length > 0) {
                        this.business = this.templateList[0]['business']
                    }
                    this.getCollectedTemplateList()
                } catch (e) {
                    this.error = true
                    errorHandler(e, this)
                } finally {
                    this.loading = false
                }
            },
            getCollectedTemplateList () {
                this.collectTemplateList = this.templateList.filter(t => t['is_add'])
                this.originalCollectTemplateList = this.collectTemplateList
            },
            search () {
                this.templateList = this.originalTemplateList.filter(item => item.name.includes(this.value))
                this.collectTemplateList = this.value ? [] : this.originalCollectTemplateList
            },
            onClickTemplate (templateId) {
                this.$store.commit('setTemplateId', templateId)
                this.$router.push({ path: `/task/create/${templateId}`, query: { templateId: templateId } })
            }
        }
    }
</script>
