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
    <div class="node-canvas">
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    export default {
        name: 'NodeCanvas'
    }
</script>
<style lang="scss" scoped>
    @import '../../../scss/config.scss';
    .node-canvas {
        width: calc(100% - 60px);
        height: calc(100% - 50px);
        background: #e1e4e8;
        background-size: 10px 10px;
    }
</style>
