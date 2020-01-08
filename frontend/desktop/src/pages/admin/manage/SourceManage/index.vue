/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="source-manage" v-bkloading="{ isLoading: loading, opacity: 1 }">
        <div class="operate-area">
            <router-link
                to="/admin/manage/source_edit/package_edit/"
                class="operate-btn bk-button bk-primary">
                {{ emptyData ? i18n.create : i18n.edit }}
            </router-link>
        </div>
        <div v-if="originList.length">
            <div class="section-title">
                <div class="title-wrapper">
                    <h4>{{i18n.mainSource}}</h4>
                    <i
                        class="title-tooltip common-icon-info"
                        v-bk-tooltips.right="i18n.sourceTip">
                    </i>
                </div>
            </div>
            <package-table v-for="value in originList" :key="value.id" :value="value"></package-table>
        </div>
        <div v-if="originList.length">
            <div class="section-title">
                <div class="title-wrapper">
                    <h4>{{i18n.localCache}}</h4>
                    <i
                        class="title-tooltip common-icon-info"
                        v-bk-tooltips.right="i18n.cacheTip">
                    </i>
                </div>
            </div>
            <local-cache v-for="cache in cacheList" :key="cache.id" :value="cache"></local-cache>
            <NoData v-if="!cacheList.length"></NoData>
        </div>
        <div class="empty-data" v-if="emptyData">
            <p>{{i18n.noData}}<router-link to="/admin/manage/source_edit/package_edit/">{{i18n.create}}</router-link>{{i18n.sourceManage}}</p>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import PackageTable from './PackageTable.vue'
    import LocalCache from './LocalCache.vue'
    import NoData from '@/components/common/base/NoData.vue'

    export default {
        name: 'SourceManage',
        components: {
            PackageTable,
            LocalCache,
            NoData
        },
        data () {
            return {
                emptyData: false,
                originList: [],
                cacheList: [],
                loading: true,
                i18n: {
                    create: gettext('新建'),
                    edit: gettext('编辑'),
                    noData: gettext('无数据，'),
                    sourceManage: gettext('远程插件包源'),
                    mainSource: gettext('主包源'),
                    localCache: gettext('本地缓存'),
                    sourceTip: gettext('远程插件包存储源，可以配置多个，注意插件包根模块名称不能冲突'),
                    cacheTip: gettext('可选配置，所有远程插件源都可以同步到本地进行缓存，避免在不能访问远程插件源时无法加载标准插件')
                }
            }
        },
        created () {
            this.loadData()
        },
        methods: {
            ...mapActions('manage', [
                'loadPackageSource'
            ]),
            async loadData () {
                this.loading = true
                try {
                    const data = await this.loadPackageSource()
                    if (data.objects.length === 0) {
                        this.emptyData = true
                    } else {
                        this.transformData(data.objects)
                    }
                } catch (err) {
                    errorHandler(err, this)
                } finally {
                    this.loading = false
                }
            },
            transformData (data) {
                const originList = []
                const cacheList = []
                data.forEach(item => {
                    if (item.category === 'origin') {
                        originList.push(item)
                    } else {
                        cacheList.push(item)
                    }
                })
                this.originList = originList
                this.cacheList = cacheList
            }
        }
    }
</script>
<style lang="scss" scoped>
    .source-manage {
        padding: 20px 60px 60px;
        min-height: calc(100% - 80px);
        background: #f4f7fa;
    }
    .operate-area {
        .operate-btn {
            height: 32px;
            line-height: 32px;
        }
    }
    .section-title {
        margin: 20px 0;
        font-size: 14px;
        .title-wrapper {
            display: flex;
            align-items: center;
        }
        h4 {
            display: inline-block;
            margin: 0;
            color: #313238;
            line-height: 1;
        }
        .title-tooltip {
            display: inline-block;
            margin-left: 10px;
            color: #c4c6cc;
            font-size: 16px;
            &:hover {
                color: #f4aa1a;
            }
        }
    }
    .empty-data {
        margin-top: 300px;
        font-size: 14px;
        color: #c4c6cc;
        text-align: center;
        a {
            color: #3a84ff;
        }
    }
    .page-manage {
        .no-data-wrapper {
            margin-top: 30px;
            background: transparent;
            color: #c4c6cc;
        }
    }
</style>
