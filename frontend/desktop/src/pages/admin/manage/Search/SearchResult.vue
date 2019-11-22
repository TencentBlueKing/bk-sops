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
    <div class="search-result">
        <div class="search-input">
            <bk-input v-model="searchStr" right-icon="bk-icon icon-search" @change="onSearch"></bk-input>
        </div>
        <div class="title">
            <h3>{{ i18n.title }}</h3>
            <span>{{ i18n.find }}</span>{{ 0 }}<span>{{ i18n.result }}</span>
        </div>
    </div>
</template>
<script>
    import tools from '@/utils/tools.js'

    export default {
        name: 'SearchResult',
        props: {
            keyword: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                searchStr: this.keyword,
                i18n: {
                    find: gettext('找到约'),
                    result: gettext('条结果')
                }
            }
        },
        created () {
            this.onSearch = tools.debounce(this.searchHandler, 500)
        },
        methods: {
            searchHandler () {
            }
        }
    }
</script>
<style lang="scss" scoped>
    .search-result {
        margin: 0 60px;
    }
</style>
