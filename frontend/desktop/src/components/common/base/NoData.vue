/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="no-data-wrapper">
        <bk-exception :type="type || 'empty'" scene="part">
            <slot>{{ message || $t('没有数据') }}</slot>
        </bk-exception>
    </div>
</template>
<script>
    export default {
        name: 'NoData',
        props: ['message', 'type']
    }
</script>
<style lang="scss" scoped>
    .no-data-wrapper {
        display: table;
        width: 100%;
        height: 100%;
        color: #999999;
        background: #ffffff;
    }
    // 异常提示固定高度
    .bk-exception {
        height: 280px;
        justify-content: center;
    }
</style>
