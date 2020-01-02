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
    <div class="base-collapse">
        <div :class="['header-wrapper', { actived: showContent }]" @click="onHeaderClick">
            <slot name="header"></slot>
            <i class="common-icon-arrow-down toggle-arrow"></i>
        </div>
        <div class="content-wrapper clearfix" v-show="showContent">
            <slot name="content"></slot>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    export default {
        name: 'BaseCollapse',
        props: {
            isCollapse: {
                type: Boolean,
                default: true
            }
        },
        data () {
            return {
                showContent: !this.isCollapse
            }
        },
        watch: {
            isCollapse (val) {
                this.showContent = !val
            }
        },
        methods: {
            onHeaderClick () {
                this.showContent = !this.showContent
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '../../../scss/config.scss';
.base-collapse {
    .header-wrapper {
        position: relative;
        padding: 0 24px;
        height: 50px;
        line-height: 50px;
        background: $blueDashBg;
        border-bottom: 1px solid $commonBorderColor;
        cursor: pointer;
        &:hover {
            background: $blueDarkBg;
        }
        &:first-child {
            border-top: 1px solid $commonBorderColor;
        }
        &.actived {
            .toggle-arrow {
                transform: rotate(-180deg);
            }
        }
    }
    .toggle-arrow {
        position: absolute;
        font-size: 12px;
        top: 20px;
        right: 20px;
        transition: transform 0.2s ease-in-out;
    }
    .content-wrapper {
        padding: 10px;
    }
}
</style>
