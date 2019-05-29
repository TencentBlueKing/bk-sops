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
    <div class="page-statistics">
        <navi-header :routers="dataDimension" :title="i18n.operationData"></navi-header>
        <div class="statistics-content">
            <div class="content-wrapper" v-if="reloadComponent">
                <router-view></router-view>
            </div>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import NaviHeader from '../components/NaviHeader.vue'

    const DATA_DIMENSION = [
        {
            text: gettext('流程统计'),
            name: 'statisticsTemplate',
            path: '/admin/statistics/template/'
        },
        {
            text: gettext('任务统计'),
            name: 'statisticsInstance',
            path: '/admin/statistics/instance/'
        },
        {
            text: gettext('标准插件统计'),
            name: 'statisticsAtom',
            path: '/admin/statistics/atom/'
        },
        {
            text: gettext('轻应用统计'),
            name: 'statisticsAppmaker',
            path: '/admin/statistics/appmaker/'
        }
    ]

    export default {
        name: 'Statistics',
        components: {
            NaviHeader
        },
        data () {
            return {
                dataDimension: DATA_DIMENSION,
                i18n: {
                    operationData: gettext('运营数据')
                },
                path: this.$router.currentRoute.path,
                reloadComponent: true
            }
        },
        watch: {
            '$route' (to, from) {
                this.reloadComponent = false
                this.path = this.$router.currentRoute.path
                this.reloadComponent = true
            }
        },
        methods: {
            onGotoPath (path) {
                this.$router.push(path)
            }
        }
    }
</script>
<style lang="scss">
@import "@/scss/config.scss";
@import "@/scss/datastatistics/datastatistics.scss";
.page-statistics {
    .header-wrapper {
        min-width: 1320px;
        padding: 0 60px;
    }
    .statistics-content {
        padding: 20px 10px 0;
        min-width: 1320px;
        .template-router {
            color: #3a84ff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
    }
}
</style>
