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
    <div class="loop-rule-select">
        <div class="loop-rule-title">
            <bk-button
                :class="['rule-btn', { 'active-btn': currentWay === 'selectGeneration' }]"
                @click="onSwitchWay('selectGeneration')">
                {{ i18n.selectGeneration }}
            </bk-button>
            <bk-button
                :class="['rule-btn', 'manual-input-btn', { 'active-btn': currentWay === 'manualInput' }]"
                @click="onSwitchWay('manualInput')">
                {{ i18n.manualInput }}
            </bk-button>
        </div>
        <div class="content-wrapper">
            <!-- 自动生成 -->
            <bk-tab
                v-show="currentWay === 'selectGeneration'"
                :type="'fill'"
                :size="'small'"
                :active-name="tabName"
                @tab-changed="tabChanged">
                <bk-tabpanel
                    v-for="(item, index) in autoRuleList"
                    :key="index"
                    :name="item.key"
                    :title="item.title">
                    <div class="tabpanel-container">
                        <div class="radio-group">
                            <div class="radio-item loop-radio">
                                <input
                                    :id="'loop' + item.key"
                                    v-model.number="item.radio"
                                    :value="0"
                                    :name="item.key"
                                    class="ui-radio"
                                    type="radio" />
                                <label
                                    class="ui-label"
                                    :for="'loop' + item.key"
                                    @click.stop="onAutoWaySwitch(index, '0')">
                                    {{ autoWay.loop.name }}
                                </label>
                            </div>
                            <div class="radio-item appoint-radio">
                                <input
                                    :id="'appoint' + item.key"
                                    v-model.number="item.radio"
                                    type="radio"
                                    class="ui-radio"
                                    :value="1"
                                    :name="item.key" />
                                <label
                                    class="ui-label"
                                    :for="'appoint' + item.key"
                                    @click.stop="onAutoWaySwitch(index, '1')">
                                    {{ autoWay.appoint.name }}
                                </label>
                            </div>
                        </div>
                        <!-- 循环 -->
                        <div
                            v-if="item.radio === 0"
                            class="loop-select-bd">
                            {{ item.key !== 'week' ? autoWay.loop.start : autoWay.loop.startWeek }}
                            <BaseInput
                                v-model.number="item.loop.start"
                                v-validate="item.loop.reg"
                                :name="item.key + 'Rule'"
                                class="loop-time"
                                @blur="renderRule()" />
                            {{ item.key !== 'week' ? item.title : ''}}{{ autoWay.loop.center }}
                            <BaseInput
                                v-model.number="item.loop.inter"
                                v-validate="{ required: true, integer: true }"
                                name="interval"
                                class="loop-time"
                                @blur="renderRule()" />
                            {{ item.key !== 'week' ? item.title : i18n.dayName }}{{ autoWay.loop.end }}
                            <!-- 星期说明 -->
                            <i
                                v-if="item.key === 'week'"
                                v-bktooltips.right="i18n.monthTips"
                                class="common-icon-tooltips month-tips"></i>
                            <!-- startInput 错误提示 -->
                            <div
                                v-show="errors.has(item.key + 'Rule') || errors.has('interval')"
                                class="local-error-tip error-msg">
                                {{ errors.first(item.key + 'Rule') || errors.first('interval') }}
                            </div>
                        </div>
                        <!-- 指定 -->
                        <div
                            v-else
                            class="appoint-select-bd">
                            <div
                                v-for="(box, i) in item.checkboxList"
                                :key="i"
                                class="ui-checkbox-group">
                                <input
                                    :id="item.key + 'box' + i"
                                    v-model="box.checked"
                                    type="checkbox"
                                    class="ui-checkbox-input"
                                    @change="renderRule">
                                <label
                                    class="ui-checkbox-label"
                                    :for="item.key + 'box' + i">
                                    <span class="ui-checkbox-icon"></span>
                                    <span class="ui-checkbox-tex"> {{ box.value | addZero(item.key) }}</span>
                                </label>
                            </div>
                        </div>
                        <div class="expression">
                            {{ i18n.expression }} {{ expressionShowText }}
                            <span
                                class="clear-selected"
                                @click.stop="clearRule">
                                {{ i18n.clearSelected }}
                            </span>
                        </div>
                    </div>
                </bk-tabpanel>
            </bk-tab>
            <!-- 手动输入 -->
            <!-- @input="onInputName" @blur="onInputBlur" @enter="onInputBlur"-->
            <div
                v-show="currentWay === 'manualInput'"
                class="hand-input">
                <BaseInput
                    v-model="periodicCron"
                    v-validate="{ required: true, cronRlue: true }"
                    name="periodicCron"
                    class="step-form-content-size" />
            </div>
        </div>
        <!-- 说明 -->
        <bk-tooltip
            placement="bottom-end"
            class="periodic-img-tooltip">
            <i class="common-icon-tooltips"></i>
            <div slot="content">
                <img class="ui-img"
                    :src="periodicCronImg">
            </div>
        </bk-tooltip>
        <span
            v-show="errors.has('periodicCron') && currentWay === 'manualInput'"
            class="common-error-tip error-msg">{{ errors.first('periodicCron') }}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { PERIODIC_REG } from '@/constants/index.js'
    import BaseInput from '@/components/common/base/BaseInput.vue'
    const autoRuleList = [
        {
            key: 'min',
            title: gettext('分钟'),
            radio: 0,
            long: 60,
            max: 59,
            loop: {
                start: 0,
                inter: 1,
                reg: {
                    required: true,
                    regex: /^([0-9]|0[1-9]|[0-5][0-9])$/
                }
            }
        },
        {
            key: 'hour',
            title: gettext('小时'),
            radio: 0,
            long: 24,
            max: 23,
            loop: {
                start: 0,
                inter: 1,
                reg: {
                    required: true,
                    regex: /^([0-9]|0[1-9]|[0-1][0-9]|20|21|23)$/
                }
            }
        },
        {
            key: 'week',
            title: gettext('星期'),
            radio: 0,
            long: 7,
            max: 6,
            loop: {
                start: 0,
                inter: 1,
                reg: {
                    required: true,
                    regex: /^[0-6]$/
                }
            }
        },
        {
            key: 'day',
            title: gettext('日期'),
            radio: 0,
            long: 31,
            max: 31,
            loop: {
                start: 1,
                inter: 1,
                reg: {
                    required: true,
                    regex: /^([1-9]|0[1-9]|1[0-9]|2[0-9]|30|31)$/
                }
            }
        },
        {
            key: 'month',
            title: gettext('月份'),
            radio: 0,
            long: 12,
            max: 12,
            loop: {
                start: 1,
                inter: 1,
                reg: {
                    required: true,
                    regex: /^([1-9]|0[1-9]|10|11|12)$/
                }
            }
        }
    ]
    const loopStarZeroList = ['min', 'hour', 'week']
    const loopStarOneList = ['day', 'month']
    const autoWay = {
        'loop': {
            name: gettext('循环'),
            start: gettext('从第'),
            startWeek: gettext('从星期'),
            center: gettext('开始,每隔'),
            end: gettext('执行一次')
        },
        'appoint': {
            name: gettext('指定')
        }
    }
    const numberMap = {
        1: gettext('星期一'),
        2: gettext('星期二'),
        3: gettext('星期三'),
        4: gettext('星期四'),
        5: gettext('星期五'),
        6: gettext('星期六'),
        0: gettext('星期天')
    }
    export default {
        name: 'loopRuleSelect',
        components: {
            BaseInput
        },
        filters: {
            addZero (v, k) {
                return k === 'week' ? v : (v < 10 ? '0' + v : v)
            }
        },
        props: {
            manualInputValue: {
                type: String,
                default: '*/5 * * * *'
            }
        },
        data () {
            return {
                i18n: {
                    dayName: gettext('天'),
                    error_code: gettext('错误码'),
                    expression: gettext('表达式：'),
                    manualInput: gettext('手动输入'),
                    clearSelected: gettext('清空已选'),
                    selectGeneration: gettext('选择生成'),
                    placeholder: gettext('0 12 * 10-17 */11'),
                    monthTips: gettext('0 表示星期天，6 表示星期六')
                },
                periodicRule: {
                    required: true,
                    regex: PERIODIC_REG
                },
                expressionList: ['*', '*', '*', '*', '*'],
                periodicCronImg: require('@/assets/images/' + gettext('task-zh') + '.png'),
                // 规则列表
                autoRuleList: autoRuleList,
                // 循环选择方式
                autoWay: autoWay,
                // manualInput 手动 / selectGeneration 选择生成
                currentWay: 'selectGeneration',
                currentRadio: 'loop',
                tabName: 'min',
                tName: '',
                periodicCron: '',
                templateNameRule: ''
            }
        },
        computed: {
            expressionShowText () {
                return this.expressionList.join('^').replace(/\^/g, ' ')
            }
        },
        watch: {
            manualInputValue: {
                handler (v) {
                    this.periodicCron = v
                    this.setValue(v)
                },
                immediate: true
            }
        },
        created () {
            this.initializeAutoRuleListData()
            this.renderRule()
        },
        methods: {
            onSwitchWay (way) {
                this.currentWay = way
            },
            /**
             * 周期选择方式切换触发
             * @param {String} name -tab name
             */
            tabChanged (name) {
                this.tabName = name
            },
            /**
             * 周期循环方式切换,循环/指定
             * @param {Number} index - 下标
             * @param {Number} value - 改变的值
             */
            onAutoWaySwitch (index, value) {
                this.$set(this.autoRuleList[index], 'radio', Number(value))
                this.renderRule()
            },
            /**
             * 初始化数据
             * @description 根据 autoRuleList 动态插入 radio 项
             */
            initializeAutoRuleListData () {
                this.autoRuleList.forEach((item, index) => {
                    const pushArr = []
                    for (let i = 0; i < item.long; i++) {
                        const realityIndex = loopStarOneList.includes(item.key) ? i + 1 : i
                        pushArr.push({
                            name: `${item.key}${i}`,
                            checked: true,
                            v: i,
                            value: item.key !== 'week' ? realityIndex : numberMap[realityIndex]
                        })
                    }
                    this.$set(this.autoRuleList[index], 'checkboxList', pushArr)
                })
            },
            // 清空已选
            clearRule () {
                this.autoRuleList.forEach((item, index) => {
                    item.checkboxList.forEach((m, i) => {
                        m.checked = false
                    })
                    item.loop.start = loopStarZeroList.includes(item.key) ? 0 : 1
                    item.loop.inter = 1
                })
                this.renderRule()
            },
            /**
             *  渲染规则
             *  @description
             *  1. min-max/1  <=> *
             *  2. min-max/n  <=> 星/d
             *  @param {String} key --tab key
             *  @param {String} way --自动/手动
             *  @param {Number} index --下标
             */
            renderRule () {
                this.autoRuleList.map((m, i) => {
                    const { radio, loop, checkboxList, max } = m
                    let loopRule = ''
                    if (loop.start === (loopStarZeroList.includes(m.key) ? 0 : 1)) {
                        loopRule = `*/${loop.inter}`
                        if (loop.inter === 1) {
                            loopRule = '*'
                        }
                    } else {
                        loopRule = `${loop.start}-${max}/${loop.inter}`
                    }
                    const pointRule = checkboxList
                        .filter(res => res.checked)
                        .map(res => {
                            // satrt 1 时 显示 i + 1
                            return loopStarOneList.includes(m.key) ? res.v + 1 : res.v
                        })
                        .join(',') || '*'
                    const data = radio === 0 ? loopRule : pointRule
                    this.$set(this.expressionList, i, data)
                })
            },
            /**
             * 合并相近数字 1,2,3 => 1-3
             * @param {Object} arr 数字数组
             */
            mergeCloseNumber (arr) {
                if (Array.isArray(arr)) {
                    let hasMergeList = []
                    const exportList = []
                    for (let i = 0; i < arr.length; i++) {
                        if (hasMergeList.some(t => t === arr[i])) continue
                        const mergeItem = []
                        let nowValue = arr[i]
                        mergeItem.push(arr[i])
                        for (let j = i + 1; j < arr.length; j++) {
                            if (nowValue + 1 === arr[j]) {
                                mergeItem.push(arr[j])
                                nowValue = arr[j]
                                continue
                            }
                            break
                        }
                        exportList.push(mergeItem)
                        hasMergeList = [...hasMergeList, ...mergeItem]
                    }
                    return exportList.map(m => m.length > 1 ? `${m[0]}-${m[m.length - 1]}/1` : `${m[0]}`)
                } else {
                    return arr
                }
            },
            /**
             * 提交时验证表达式
             * @returns {Boolean} true/false
             */
            validationExpression () {
                let flag = true
                autoRuleList.forEach(m => {
                    if (this.$validator.errors.has(m.key + 'Rule') && this.currentWay === 'selectGeneration') {
                        this.tabName = m.key
                        flag = false
                    }
                })
                if (this.currentWay === 'manualInput' && this.$validator.errors.has('periodicCron')) {
                    this.currentWay = 'manualInput'
                    flag = false
                }
                return {
                    check: flag,
                    rule: this.currentWay === 'manualInput' ? this.periodicCron : this.expressionShowText
                }
            },
            /**
             * 根据表达式设置选中状态
             * @param {String} v
             * 目前传入值仅支持 4 中形式
             * 1. *
             * 2. min-max/d
             * 3. d,d,d,d
             * 4. ※/d <===> min-max/d
             */
            setValue (setValue) {
                this.$nextTick(() => {
                    const periodicList = setValue.split(' ')
                    periodicList.forEach((m, i) => {
                        const item = this.autoRuleList[i]
                        if (m === '*') {
                            item.radio = 0
                            item.checkboxList.forEach(t => {
                                t.checked = true
                            })
                        } else if (m.indexOf('/') !== -1 && m.split('/')[0].split('-')[1] * 1 === item.max) {
                            // min-max/d
                            item.radio = 0
                            item.loop.start = m.split('/')[0].split('-')[0] * 1
                            item.loop.inter = m.split('/')[1] * 1
                        } else if (m.indexOf('*/') !== -1) {
                            // */d
                            item.radio = 0
                            item.loop.start = loopStarZeroList.includes(item.key) ? 0 : 1
                            item.loop.inter = m.split('/')[1] * 1
                        } else if (!/[^(\d{1,2},)]|[^(\d{1,2})]/g.test(m)) {
                            // d,d,d,d
                            item.radio = 1
                            item.checkboxList.forEach((box, boxIndex) => {
                                box.checked = m.split(',').some(s => {
                                    return loopStarOneList.includes(item.key) ? s * 1 - 1 === box.v * 1 : s * 1 === box.v * 1
                                })
                            })
                        } else {
                            // 匹配不到
                            this.currentWay = 'manualInput'
                        }
                    })
                    this.renderRule()
                })
            }
        }
    }
</script>
<style lang="scss" scoped>
@import "@/scss/config.scss";
$blueBtnBg: #c7dcff;
$colorBalck: #313238;
$colorBlue: #3a84ff;
$colorGrey: #63656e;
$bgBlue: #3a84ff;

.ui-checkbox-group {
    margin-top: 20px;
    margin-right: 18px;
    display: inline-block;
    .ui-checkbox-input {
        display: none;
    }
    .ui-checkbox-icon {
        box-sizing: border-box;
        display: inline-block;
        position: relative;
        width: 16px;
        height: 16px;
        border: 1px solid #979BA5;
        text-align: center;
        padding-left: 12px;
        line-height: 1;
    }
    .ui-checkbox-label {
        user-select: none;
        cursor: pointer;
        color: $colorGrey;
        .ui-checkbox-tex,
        .ui-checkbox-icon {
            vertical-align: middle;
        }
    }
    .ui-checkbox-input:checked + .ui-checkbox-label > .ui-checkbox-icon::after {
        content: "";
        position: absolute;
        left: 2px;
        top: 2px;
        height: 4px;
        width: 8px;
        border-left: 2px solid;
        border-bottom: 2px solid;
        border-color: #ffffff;
        -webkit-transform: rotate(-45deg);
        transform: rotate(-45deg);
    }
    .ui-checkbox-input:checked + .ui-checkbox-label > .ui-checkbox-icon {
        background: $bgBlue;
        border-color: $bgBlue;
    }
}
.local-error-tip {
    margin-top: 10px;
    font-size: 14px;
    line-height: 1;
    color: #ff5757;
}
.loop-rule-select {
    position: relative;
    width: 500px;
    .loop-rule-title {
        white-space: nowrap;
        .rule-btn {
            width: 50%;
            border: 1px solid $commonBorderColor;
            border-radius: 0;
        }
        .manual-input-btn {
            margin-left: -5px;
        }
        .active-btn {
            background-color: $blueBtnBg;
            border-color: $blueDefault;
            color: $blueDefault;
        }
    }
    // content
    .content-wrapper {
        margin-top: 18px;
        background-color: $whiteDefault;
        /deep/ .tab2-nav-item {
            width: 20%;
            border-bottom: 1px solid $commonBorderColor;
            line-height: 40px !important;
            &:not(:first-child) {
                border-left: 1px solid $commonBorderColor !important;
            }
        }
        /deep/.bk-tab2-nav .active {
            border-bottom: none;
            border-right: none !important;
        }
        /deep/ .bk-tab2 {
            border: 1px solid $commonBorderColor;
        }
        .tabpanel-container {
            padding: 20px;
            .radio-item {
                display: inline-block;
                &:not(:first-child) {
                    margin-left: 48px;
                }
                .ui-label {
                    font-size: 14px;
                    color: $colorGrey;
                    &::before {
                        content: "\a0"; /*不换行空格*/
                        display: inline-block;
                        vertical-align: middle;
                        width: 1em;
                        height: 1em;
                        margin-right: 0.4em;
                        border-radius: 50%;
                        border: 1px solid $commonBorderColor;
                        text-indent: 0.15em;
                        line-height: 1;
                        box-sizing: border-box;
                        font-size: 16px;
                    }
                }
                .ui-radio {
                    position: absolute;
                    clip: rect(0, 0, 0, 0);
                }
                .ui-radio:checked + .ui-label::before {
                    background-color: $blueDefault;
                    background-clip: content-box;
                    box-sizing: border-box;
                    padding: 0.2em;
                }
            }
            .loop-select-bd {
                margin-top: 18px;
                font-size: 14px;
                color: $colorBalck;
                .loop-time {
                    margin: 0 10px;
                    width: 46px;
                }
                .month-tips {
                    color: #c4c6cc;
                    font-size: 14px;
                    &:hover {
                        color: #f4aa1a;
                    }
                }
            }
            .appoint-select-bd {
                margin-top: 18px;
                padding: 0 20px 20px 20px;
                border: 1px solid $commonBorderColor;
            }
            .expression {
                margin-top: 20px;
                font-size: 14px;
                word-break: break-all;
                .clear-selected {
                    margin-left: 20px;
                    color: $colorBlue;
                    cursor: pointer;
                }
            }
        }
    }
    .periodic-img-tooltip {
        position: absolute;
        right: -18px;
        top: 10px;
        color: #c4c6cc;
        font-size: 14px;
        z-index: 4;
        &:hover {
            color: #f4aa1a;
        }
        /deep/ .bk-tooltip-arrow {
            display: none;
        }
        /deep/ .bk-tooltip-inner {
            max-width: 520px;
            padding: 0px;
            border: none;
            background-color: transparent;
        }
    }
}
</style>
