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
    <div class="ip-search-input">
        <input
            type="text"
            class="search-input"
            :placeholder="placeholder"
            v-model="keyword"
            @input="onInputChange"/>
        <i class="bk-icon icon-search search-icon"></i>
    </div>
</template>
<script>
import '@/utils/i18n.js' // ip选择器兼容标准运维国际化

const i18n = {
    placeholder: gettext('搜索IP，多个以逗号隔开')
}

export default {
    name: 'IpSearchInput',
    props: {
        placeholder: {
            type: String,
            default: i18n.placeholder
        }
    },
    data () {
        return {
            keyword: '',
            delay: 500,
            timer: null
        }
    },
    methods: {
        onInputChange () {
            clearTimeout(this.timer)
            this.timer = setTimeout(()=>{
                this.$emit('search', this.keyword)
            }, this.delay)
        }
    }
}
</script>
<style lang="scss" scoped>
.search-input {
    padding: 0 32px 0 10px;
    width: 100%;
    height: 36px;
    line-height: 36px;
    font-size: 14px;
    border: 1px solid #c4c6cc;
    border-radius: 2px;
    outline: none;
    &:focus {
        border: 1px solid #3486ff;
        & + .search-icon {
            color: #3486ff;
        }
    }
}
.search-icon {
    position: absolute;
    right: 12px;
    top: 12px;
    color: #63656e;
    font-size: 14px;
}
</style>
