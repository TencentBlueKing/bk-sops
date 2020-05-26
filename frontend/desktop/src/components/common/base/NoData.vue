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
    <div class="no-data-wrapper">
        <div class="no-data">
            <i class="common-icon-no-data"></i>
            <p class="no-data-wording">
                <slot>{{ message || $t('无数据') }}</slot>
            </p>
        </div>
    </div>
</template>
<script>
    export default {
        name: 'NoData',
        props: {
            message: {
                type: String,
                default () {
                    return ''
                }
            }
        }
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
    .no-data {
        display: table-cell;
        vertical-align: middle;
        text-align: center;
    }
    .common-icon-no-data {
        font-size: 40px;
    }
    .no-data-wording {
        margin-top: 20px;
        font-size: 14px;
    }
</style>
