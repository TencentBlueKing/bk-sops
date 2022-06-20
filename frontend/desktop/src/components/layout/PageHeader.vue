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
    <div class="page-header">
        <slot>
            <ul class="tab-list" v-if="tabList.length">
                <li
                    v-for="(item, index) in tabList"
                    :key="index"
                    :class="['tab-item', { 'active': $route.name === item.routerName }]"
                    @click="tabChange(item)">
                    {{ item.name }}
                </li>
            </ul>
        </slot>
        <div class="expand">
            <slot name="expand"></slot>
        </div>
    </div>
</template>

<script>
    import '@/utils/i18n.js'
    export default {
        name: 'PageHeader',
        inject: ['reload'],
        props: {
            selfReload: {
                type: Boolean,
                default: false
            },
            tabList: {
                type: Array,
                default: () => ([])
            }
        },
        methods: {
            tabChange (tabItem) {
                if (this.$route.name === tabItem.routerName) {
                    if (this.selfReload) {
                        this.$emit('tabChange', tabItem)
                    } else {
                        this.reload()
                    }
                    return false
                }
                this.$router.push({ name: tabItem.routerName, params: tabItem.params, query: tabItem.query })
            }
        }
    }
</script>

<style lang='scss' scoped>
.page-header {
    position: relative;
    height: 48px;
    border-bottom: 1px solid #dcdee5;
    box-shadow: 0 3px 4px 0 rgba(64, 112, 203, 0.06);
    background: #ffffff;
    z-index: 101;
    .tab-list {
        margin-left: 26px;
        float: left;
        display: flex;
        position: relative;
        line-height: 46px;
        .tab-item {
            padding: 0 20px;
            min-width: 80px;
            height: 100%;
            font-size: 14px;
            cursor: pointer;
            text-align: center;
            &.active {
                color: #3a84ff;
                border-bottom: 2px solid #3a84ff;
            }
        }
    }
    .expand {
        float: right;
    }
}
</style>
