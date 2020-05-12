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
    <li
        :class="[
            'card-item',
            { 'permission-disable': isApplyPermission },
            { 'selected': selected }]"
        @click="onCardClick">
        <div v-if="!iconText" class="card-icon">
            {{ displayName.trim().substr(0,1).toUpperCase() }}
        </div>
        <div
            v-else
            :class="[
                'card-icon',
                'type-icon',
                { 'zh-en': lang === 'en' }]">
            {{ iconText }}
        </div>
        <div class="card-content">
            <p class="text">{{ displayName }}</p>
        </div>
        <div v-if="isApplyPermission" class="apply-permission-mask">
            <bk-button theme="primary" size="small">{{i18n.applyPermission}}</bk-button>
        </div>
        <div v-if="showDelete" class="card-delete common-icon-dark-circle-close" @click.stop="onDeleteCard"></div>
    </li>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState } from 'vuex'
    export default {
        name: 'BaseCard',
        props: {
            data: {
                type: Object,
                default: () => ({})
            },
            isApplyPermission: {
                type: Boolean,
                default: false
            },
            selected: {
                type: Boolean,
                default: false
            },
            showDelete: {
                type: Boolean,
                default: false
            },
            setName: {
                type: String,
                default: ''
            },
            iconText: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                i18n: {
                    applyPermission: gettext('申请权限')
                }
            }
        },
        computed: {
            ...mapState({
                lang: state => state.lang
            }),
            displayName () {
                return this.setName || this.data.name
            }
        },
        methods: {
            onDeleteCard () {
                this.$emit('onDeleteCard', this.data)
            },
            onCardClick () {
                this.$emit('onCardClick', this.data)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/multiLineEllipsis.scss';
.card-item {
    display: table;
    position: relative;
    margin-top: 20px;
    margin-right: 16px;
    width: 278px;
    height: 60px;
    cursor: pointer;
    background: #f0f1f5;
    border-radius: 2px;
    &:not(.permission-disable, .selected):hover {
        .card-icon {
            background: #b9bbc1;
        }
        .card-content {
            background: #e3e5e9;
            .text::after {
                background: #e3e5e9;
            }
        }
    }
    .card-icon {
        display: table-cell;
        width: 60px;
        min-width: 60px;
        height: 60px;
        line-height: 60px;
        text-align: center;
        font-size: 32px;
        color: #ffffff;
        vertical-align: middle;
        background: #c4c6cc;
        border-top-left-radius:2px;
        border-bottom-left-radius:2px;
        &.type-icon {
            word-break: break-word;
            font-size: 16px;
            line-height: normal;
            padding: 8px;
        }
        &.zh-en {
            font-size: 14px;
        }
    }
    .card-content {
        display: table-cell;
        padding: 12px 33px 12px 12px;
        width: 100%;
        height: 60px;
        vertical-align: middle;
        .text {
            font-size: 12px;
            color: #313238;
            word-break: break-all;
            @include multiLineEllipsis(12px, 2);
            line-height: 1.5em;
            max-height: 3em;
            &:after {
                background: #f0f1f5;
            }
        }
    }
     &.permission-disable {
        background: #f7f7f7;
        border: 1px solid #dcdee5;
        height: auto;
        .card-icon {
            color: #dcdee5;
            background: #f7f7f7;
            border-right: 1px solid #dcdee5;
        }
        .card-content {
            border-left: none;
        }
        .text {
            color: #c4c6cc;
            &:after {
                background: #f7f7f7;
            }
        }
        .apply-permission-mask {
            background: rgba(255, 255, 255, 0.6);
            text-align: center;
        }
        .bk-button {
            height: 32px;
            line-height: 30px;
        }
        &:hover .apply-permission-mask {
            display: block;
        }
    }
    &.selected {
        .card-icon {
            background: #666a7c;
        }
        .text, .card-content {
            background: #838799;
            color: #ffffff;
            &:after {
                background: #838799;
            }
        }
        &:hover {
            .text::after {
                background: #838799;
            }
        }
    }
    &:hover {
        .card-delete {
            display: block;
        }
    }
    .apply-permission-mask {
        display: none;
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 60px;
        line-height: 60px;
        text-align: center;
    }
    .card-delete {
        display: none;
        position: absolute;
        right: -8px;
        top: -8px;
        font-size: 16px;
        color: #838799;
        background: #ffffff;
        border-radius: 50%;
        border: 2px solid #ffffff;
    }
}
</style>
