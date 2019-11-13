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
    <div class="page-manage">
        <base-title
            class="title"
            type="router"
            :tab-list="routers"
            :title="title">
        </base-title>
        <router-view></router-view>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    const ROUTERS = [
        {
            name: gettext('远程插件包源管理'),
            routerName: 'sourceManage'
        },
        {
            name: gettext('远程插件同步'),
            routerName: 'sourceSync'
        }
    ]

    export default {
        name: 'Manage',
        components: {
            BaseTitle
        },
        data () {
            return {
                i18n: {
                    manage: gettext('后台管理'),
                    editSource: gettext('编辑包源')
                }
            }
        },
        computed: {
            routers () {
                return ['packageEdit', 'cacheEdit'].includes(this.$route.name) ? [] : ROUTERS
            },
            title () {
                return ['packageEdit', 'cacheEdit'].includes(this.$route.name) ? this.i18n.editSource : this.i18n.manage
            }
        }
    }
</script>
<style lang="scss" scoped>
    .page-manage {
        padding: 0 60px;
        min-width: 1320px;
        height: 100%;
        background: #f4f7fa;
        .header-wrapper {
            margin: 0 60px 0;
        }
    }
</style>
