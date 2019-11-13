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
    <div class="task-manage">
        <base-title
            type="router"
            :title="title"
            :tab-list="titleTabList">
        </base-title>
        <router-view></router-view>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    export default {
        name: 'TaskManage',
        components: {
            BaseTitle
        },
        data () {
            return {
                titleTabList: [
                    { name: gettext('任务记录'), routerName: 'taskList' },
                    { name: gettext('周期任务'), routerName: 'periodicTemplate' }
                ],
                title: gettext('任务管理')
            }
        }
    }
</script>
<style lang="scss" scoped>
.task-manage {
    padding: 0 60px;
}
</style>
