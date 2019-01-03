/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="node-preview-wrapper" v-bkloading="{isLoading: loading, opacity: 1}">
        <PipelineCanvas
            v-if="!loading"
            :isMenuBarShow="false"
            :isConfigBarShow="false"
            :isEdit="false"
            :canvasData="canvasData">
        </PipelineCanvas>
    </div>
</template>
<script>
import '@/utils/i18n.js'
import PipelineCanvas from '@/components/common/PipelineCanvas/index.vue'
export default {
    name: 'NodePreview',
    components: {
        PipelineCanvas
    },
    props: ['canvasData', 'loading']
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
    .node-preview-wrapper {
        height: 550px;
        overflow: hidden;
        /deep/ .node-canvas {
            width: 100%;
            height: 100%;
            background: $whiteDefault;
        }
    }
</style>
