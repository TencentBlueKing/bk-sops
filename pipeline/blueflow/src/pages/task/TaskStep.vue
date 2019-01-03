/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <div class="step-wrapper">
        <ul class="step-list">
            <li
                :class="{
                    'step-item': true,
                    'finished': allFinished || index < currentStepIndex,
                    'actived': !allFinished && index === currentStepIndex
                }"
                v-for="(item, index) in list"
                :key="index">
                <span class="common-icon-done-thin step-done" v-if="allFinished || index < currentStepIndex"></span>
                <span class="order" v-else>{{index + 1}}</span>
                <span class="name">{{item.name}}</span>
                <span class="dot" v-if="index !== list.length - 1">......</span>
            </li>
        </ul>
    </div>
</template>
<script>
import '@/utils/i18n.js'
export default {
    name: 'TaskCreateStep',
    props: ['list', 'currentStep', 'allFinished'],
    data () {
        return {}
    },
    computed: {
        currentStepIndex () {
            return this.getCurrentStepIndex()
        }
    },
    methods: {
        getCurrentStepIndex () {
            let currentStepIndex = 0
            this.list.some((item, index) => {
                if (item.step === this.currentStep) {
                    currentStepIndex = index
                    return true
                }
            })
            return currentStepIndex
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.step-wrapper {
    background: $blueNavBg;
    border: 1px solid $stepNavColor;
    .step-list {
        display: flex;
        margin: 0 auto;
        width: 1200px;
    }
    .step-item {
        display: inline-block;
        flex: 1;
        height: 60px;
        line-height: 60px;
        font-size: 14px;
        font-weight: bold;
        color: $greyDark;
        text-align: center;
        .step-done {
            display: inline-block;
            width: 38px;
            height: 38px;
            line-height: 38px;
            font-size: 16px;
            color: $whiteDefault;
            background: $blueDefault;
            border-radius: 50%;
            text-align: center;
        }
        .order {
            display: inline-block;
            width: 38px;
            height: 38px;
            line-height: 38px;
            font-size: 16px;
            text-align: center;
            border: 2px solid $greyDark;
            border-radius: 50%;
        }
        .name {
            margin-left: 10px;
        }
        .dot {
            float: right;
        }
        &.actived {
            color: $blueDefault;
            .order {
                border-color: $blueDefault;
            }
        }
        &.finished {
            color: $blueDefault;
        }
    }
}
</style>

