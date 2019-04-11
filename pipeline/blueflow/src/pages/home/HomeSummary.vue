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
    <div class="summary-content clearfix">
        <div class="summary-item clearfix">
            <div class="count-title">
                <div>
                    <router-link
                        class="summary-module"
                        :to="`/taskflow/home/${cc_id}`">
                        <i class="common-icon-clock-inversion module-icon"></i>
                        <span class="module-entry">{{i18n.enter}}</span>
                    </router-link>
                    <h4 class="title">{{i18n.executeTask}}</h4>
                    <p class="num">{{summaryData.executeStatus.total}}{{i18n.times}}</p>
                </div>
            </div>
            <ul class="count-detail task-execute">
                <li
                    v-for="item in summaryData.executeStatus.groups"
                    :key="item.code"
                    class="item-info">
                    <span>{{item.name}}: </span>
                    <span class="value">{{item.value}}</span>
                </li>
            </ul>
            <div class="sperate-line"></div>
        </div>
        <div class="summary-item clearfix">
            <div class="count-title">
                <router-link
                    class="summary-module"
                    :to="`/template/new/${cc_id}`">
                    <i class="common-icon-circulation module-icon"></i>
                    <span class="module-entry">{{i18n.enter}}</span>
                </router-link>
                <h4 class="title">{{i18n.template}}</h4>
                <p class="num">{{summaryData.templateStatus.total}}{{i18n.num}}</p>
            </div>
            <ul class="count-detail">
                <li
                    v-for="item in summaryData.templateStatus.groups"
                    :key="item.code"
                    class="item-info">
                    <span>{{item.name}}: </span>
                    <span class="value">{{item.value}}</span>
                </li>
            </ul>
            <div class="sperate-line"></div>
        </div>
        <div class="summary-item clearfix">
            <div class="count-title">
                <router-link
                    class="summary-module"
                    :to="`/appmaker/home/${cc_id}`">
                    <i class="common-icon-box module-icon"></i>
                    <span class="module-entry">{{i18n.enter}}</span>
                </router-link>
                <h4 class="title">{{i18n.appmaker}}</h4>
                <p class="num">{{summaryData.appmakerStatus.total}}{{i18n.num}}</p>
            </div>
            <ul class="count-detail">
                <li
                    v-for="item in summaryData.appmakerStatus.groups"
                    :key="item.code"
                    class="item-info">
                    <span>{{item.name}}: </span>
                    <span class="value">{{item.value}}</span>
                </li>
            </ul>
        </div>
    </div>
</template>
<script>
import '@/utils/i18n.js'
export default {
    name: 'HomeSummary',
    props: ['cc_id', 'summaryData'],
    data () {
        return {
            i18n: {
                enter: gettext('进入'),
                executeTask: gettext('执行任务'),
                template: gettext('新建流程'),
                appmaker: gettext('轻应用'),
                times: gettext('次'),
                num: gettext('个')
            }
        }
    }
}
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
.summary-content {
    width: 1200px;
    margin: 0 auto;
    .summary-item {
        float: left;
        position: relative;
        width: 400px;
        height: 220px;
        color: $whiteDefault;
        &:hover {
            background: rgba(52, 151, 234, .25);
        }
        .sperate-line {
            position: absolute;
            right: 0;
            top: 60px;
            width: 1px;
            height: 100px;
            background: #3ea1cf;
        }
    }
    .count-title {
        float: left;
        width: 50%;
        height: 100%;
        text-align: center;
        .summary-module {
            display: inline-block;
            margin-top: 40px;
            width: 70px;
            height: 70px;
            line-height: 70px;
            text-align: center;
            color: #3c96ff;
            background: $whiteDefault;
            border-radius: 50%;
            box-shadow: -1px 1px 8px rgba(100, 100, 100, .25), 1px -1px 8px rgba(100, 100, 100, .25);
            cursor: pointer;
            .module-icon {
                display: inline-block;
                font-size: 30px;
                vertical-align: middle;
            }
            .common-icon-box {
                font-size: 34px;
            }
            .module-entry {
                display: none;
                font-size: 18px;
            }
            &:hover {
                color: $whiteDefault;
                background: $greenDark;
                .module-icon {
                    display: none;
                }
                .module-entry {
                    display: inline-block;
                }
            }
        }
        .title {
            margin: 10px 0 8px;
            font-size: 14px;
        }
        .num {
            font-size: 24px;
            font-weight: bold;
        }
    }
    .count-detail {
        float: left;
        padding: 32px 0;
        width: 50%;
        height: 100%;
        &.task-execute {
            padding: 80px 0;
        }
    }
    .item-info {
        font-size: 14px;
        height: 22px;
        line-height: 22px;
        font-size: 12px;
        .value {
            font-weight: bold;
        }
    }
}
</style>
