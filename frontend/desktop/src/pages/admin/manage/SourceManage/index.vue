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
            <bk-button
                v-if="!hasEditPerm"
                v-cursor="{ active: true }"
                theme="primary"
                class="btn-permission-disable"
                @click="applyEditPerm">
                {{ emptyData ? $t('新建') : $t('编辑') }}
            </bk-button>
            <router-link
                v-else
                :to="{ name: 'packageEdit' }"
                class="bk-button bk-primary">
                {{ emptyData ? $t('新建') : $t('编辑') }}
            </router-link>
        </div>
        <div v-if="originList.length">
            <div class="section-title">
                <div class="title-wrapper">
                    <h4>{{$t('主包源')}}</h4>
                    <i
                        class="title-tooltip common-icon-info"
                        v-bk-tooltips.right="$t('远程插件包存储源，可以配置多个，注意插件包根模块名字不能冲突')">
                    </i>
                </div>
            </div>
            <package-table v-for="value in originList" :key="value.id" :value="value"></package-table>
        </div>
        <div v-if="originList.length">
            <div class="section-title">
                <div class="title-wrapper">
                    <h4>{{$t('本地缓存')}}</h4>
                    <i
                        class="title-tooltip common-icon-info"
                        v-bk-tooltips.right="$t('可选配置，所有远程插件源都可以同步到本地进行缓存，避免在不能访问远程插件源时无法加载标准插件')">
                    </i>
                </div>
            </div>
            <local-cache v-for="cache in cacheList" :key="cache.id" :value="cache"></local-cache>
            <div class="cache-empty">
                <NoData v-if="!cacheList.length"></NoData>
            </div>
        </div>
        <div class="empty-data" v-if="emptyData">
            <p>{{$t('无数据，')}}
                <a
                    v-if="!hasEditPerm"
                    v-cursor="{ active: true }"
                    class="text-permission-disable"
                    @click="applyEditPerm">
                    {{$t('新建')}}
                </a>
                <router-link v-else :to="{ name: 'packageEdit' }">{{$t('新建')}}</router-link>
                {{$t('远程插件包源')}}
            </p>
        </div>
    </div>
</template>
<script>
    import { mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import permission from '@/mixins/permission.js'
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
        mixins: [permission],
        props: {
            hasEditPerm: Boolean,
            editPermLoading: Boolean
        },
        data () {
            return {
                emptyData: false,
                originList: [],
                cacheList: [],
                loading: true
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
            },
            applyEditPerm () {
                if (this.editPermLoading) {
                    return
                }
                this.applyForPermission(['admin_edit'])
            }
        }
    }
</script>
<style lang="scss" scoped>
    .source-manage {
        padding-top: 20px;
        min-height: calc(100% - 140px);
        background: #f4f7fa;
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
    .cache-empty {
        padding: 30px 0;
        background: #ffffff;
        border: 1px solid #dde4eb;
    }
</style>
