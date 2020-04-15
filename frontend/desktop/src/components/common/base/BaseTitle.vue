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
    <div class="base-title">
        <slot>
            <span class="title-name">{{ title }}</span>
            <ul class="base-tab-list" v-if="tabList.length">
                <li
                    v-for="(item, index) in tabList"
                    :key="index"
                    :class="['base-tab-item', { 'active': isActive(item) }]"
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
        name: 'BaseTitle',
        inject: ['reload'],
        props: {
            title: {
                type: String,
                default: ''
            },
            /**
             * type
             * router/default
             */
            type: {
                type: String,
                default: 'default'
            },
            active: {
                type: String,
                default: ''
            },
            /**
             * default:
             * tabList[index].name 显示名
             * tabList[index].key 匹配值，与 active 传入值映射
             * router:
             * tabList[index].name 显示名
             * tabList[index].routerName 匹配路由名,与当前路由有关
             */
            tabList: {
                type: Array,
                default: () => ([])
            }
        },
        methods: {
            tabChange (tabItem) {
                if (this.$route.name === tabItem.routerName) {
                    this.reload()
                    return false
                }
                if (tabItem.routerName) {
                    this.$router.push({ name: tabItem.routerName, params: tabItem.params, query: tabItem.query })
                }
                this.$emit('tabChange', tabItem.key)
            },
            isActive (tabItem) {
                if (this.type === 'router' && tabItem.routerName) {
                    return this.$route.name === tabItem.routerName
                }
                return this.active === tabItem.key
            }
        }
    }
</script>

<style lang='scss' scoped>
.base-title {
    position: relative;
    height: 60px;
    line-height: 60px;
    border-bottom: 1px solid #dde4eb;
    .title-name {
        float: left;
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
    .base-tab-list {
        margin-left: 26px;
        float: left;
        display: flex;
        position: relative;
        &:before {
            content: '';
            position: absolute;
            left: 0;
            top: 21px;
            width: 0;
            height: 20px;
            border-left: 2px solid #dde4eb;
        }
        .base-tab-item {
            margin-left: 26px;
            font-size: 14px;
            height: 100%;
            cursor: pointer;
            box-sizing: border-box;
            &.active {
                color: #3a84ff;
                border-bottom: 2px solid #3a84ff;
            }
        }
    }
    .expand {
        float: right;
        margin-top: -6px;
    }
}
</style>
