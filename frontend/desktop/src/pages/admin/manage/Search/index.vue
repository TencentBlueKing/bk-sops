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
    <div class="admin-search">
        <div v-if="!showResultComp" class="search-wrapper">
            <p class="tips">{{ i18n.tips }}</p>
            <bk-input
                v-model="searchStr"
                class="search-input"
                right-icon="bk-icon icon-search"
                @change="onSearchInput">
            </bk-input>
        </div>
        <search-result
            v-else
            :keyword="searchStr"
            @onSearch="onSearchInput">
        </search-result>
    </div>
</template>
<script>
    import tools from '@/utils/tools.js'
    import SearchResult from './SearchResult.vue'

    export default {
        name: 'AdminSearch',
        components: {
            SearchResult
        },
        data () {
            return {
                showResultComp: false,
                searchStr: '',
                i18n: {
                    tips: gettext('搜索业务名称，流程模板ID，任务ID')
                }
            }
        },
        created () {
            this.onSearchInput = tools.debounce(this.searchInputhandler, 500)
        },
        methods: {
            searchInputhandler () {
                this.showResultComp = true
            }
        }
    }
</script>
<style lang="scss" scoped>
    .admin-search {
        position: relative;
        height: calc(100% - 60px);
        overflow: hidden;
    }
    .search-wrapper {
        position: absolute;
        top: 34%;
        left: 50%;
        transform: translateX(-50%);
        width: 588px;
        .tips {
            margin-bottom: 8px;
            font-size: 12px;
            color: #63656e;
        }
        .search-input /deep/ input{
            color: #313238;
            height: 48px;
            line-height: 48px;
        }
    }
</style>
