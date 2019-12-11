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
        <div class="base-title-header">
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
            <ul class="expand">
                <slot name="expand"></slot>
            </ul>
        </div>
        <div class="base-tab-content">
            <slot name="content" v-bind:active="activeItem"></slot>
        </div>
    </div>
</template>

<script>
    import '@/utils/i18n.js'
    export default {
        name: 'BaseTitle',
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
        data () {
            return {
            }
        },
        computed: {
            activeItem () {
                if (this.type === 'router') {
                    return this.tabList.find(m => m.routerName === this.$route.name)
                }
                return this.tabList.find(m => m.key === this.active)
            }
        },
        methods: {
            tabChange (tabTtem) {
                if (tabTtem.routerName) {
                    this.$router.push({ name: tabTtem.routerName, params: tabTtem.params, query: tabTtem.query })
                }
                this.$emit('tabChange', tabTtem.key)
            },
            isActive (tabTtem) {
                if (this.type === 'router' && tabTtem.routerName) {
                    return this.$route.name === tabTtem.routerName
                }
                return this.active === tabTtem.key
            }
        }
    }
</script>

<style lang='scss' scoped>
.base-title-header {
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
        height: 60px;
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
        display: inline-block;
        height: 60px;
    }
}
</style>
