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
    <div class="panel-nodata">
        <p class="text">{{ text }}</p>
        <div class="des">
            <slot></slot>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    export default {
        name: 'PanelNodata',
        props: {
            text: {
                type: String,
                default: gettext('暂无数据')
            }
        },
        data () {
            return {
            }
        },
        created () {
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.panel-nodata {
    min-height: 134px;
    padding-top: 40px;
    .text {
        text-align: center;
        font-size: 14px;
        color: #63656e;
    }
    .des {
        margin-top: 15px;
        text-align: center;
        color: #63656e;
        font-size: 12px;
    }
}
</style>
