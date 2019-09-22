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
    <div class="list-wrapper-title">
        <span class="list-wrapper-name">{{ title }}</span>
    </div>
</template>

<script>
    import '@/utils/i18n.js'
    export default {
        name: 'BaseTitle',
        props: ['title']
    }
</script>

<style lang='scss' scoped>
.list-wrapper-title {
    position: relative;
    height: 60px;
    line-height: 60px;
    border-bottom: 1px solid #dde4eb;
    .list-wrapper-name {
        margin-left: 12px;
        font-size: 14px;
        font-weight:600;
        color: #313238;
        &:before {
            content: '';
            position: absolute;
            left: 0;
            top: 21px;
            width: 0;
            height: 20px;
            border-left: 2px solid #a3c5fd;
        }
    }
}
</style>
