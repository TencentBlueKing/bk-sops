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
        <p class="exception-img">
            <img :src="type === 'search-empty' ? searchEmptyUrl : notDataUrl" alt="">
        </p>
        <p class="text-title">{{ message || $t('暂无数据') }}</p>
        <p class="text-subtitle" v-if="type === 'search-empty'">
            {{ $t('可以尝试 调整关键词 或' ) }}
            <bk-button title="primary" :text="true" class="clear" @click="$emit('searchClear')">
                {{ $t('清空筛选条件') }}
            </bk-button>
        </p>
        <slot></slot>
    </div>
</template>
<script>
    export default {
        name: 'NoData',
        props: {
            type: {
                type: String,
                default: 'empty'
            },
            message: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                notDataUrl: require('@/assets/images/not-data.png'),
                searchEmptyUrl: require('@/assets/images/search-empty.png')
            }
        }
    }
</script>
<style lang="scss" scoped>
    .no-data-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 280px;
        font-size: 14px;
        background: #ffffff;
        .exception-img {
            margin-bottom: 8px;
            img {
                width: 220px;
            }
        }
        .text-title {
            color: #63656e;
            line-height: 22px;
        }
        .text-subtitle {
            color: #979ba5;
            margin-top: 8px;
            .text-btn {
                color: #3a84ff;
            }
        }
    }
</style>
