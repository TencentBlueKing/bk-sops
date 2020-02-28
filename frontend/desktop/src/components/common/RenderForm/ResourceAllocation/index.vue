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
    <div class="resource-allocation">
        <resource-list
            v-if="!showFilter"
            :show-filter.sync="showFilter">
        </resource-list>
        <resource-filter
            v-else
            :show-filter.sync="showFilter">
        </resource-filter>
    </div>
</template>
<script>
    import ResourceList from './ResourceList.vue'
    import ResourceFilter from './ResourceFilter.vue'

    export default {
        name: 'ResourceAllocation',
        components: {
            ResourceList,
            ResourceFilter
        },
        data () {
            return {
                showFilter: false
            }
        }
    }
</script>
<style style="scss" scoped>
    .resource-allocation {
        width: 800px;
        background: #ffffff;
    }
</style>
