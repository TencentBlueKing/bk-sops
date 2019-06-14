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
            <bk-button :class="['rule-btn', { 'active-btn': currentWay === 'selectGeneration' }]"
                @click="onSwitchWay('selectGeneration')">
                {{ i18n.selectGeneration }}
            </bk-button>
            <bk-button :class="['rule-btn', 'manual-input-btn', { 'active-btn': currentWay === 'manualInput' }]"
                @click="onSwitchWay('manualInput')">
                {{ i18n.manualInput }}
            </bk-button>
        </div>
        <div class="content-wrapper">
            <!-- 自动生成 -->
            <bk-tab v-if="currentWay === 'selectGeneration'"
                :type="'fill'"
                :size="'small'"
                :active-name="tabName"
                @tab-changed="tabChanged">
                <bk-tabpanel v-for="(item, index) in autoRuleList"
                    :key="index"
                    :name="item.k"
                    :title="item.title">
                    <div class="tabpanel-container">
                        <div class="radio-group">
                            <div class="radio-item loop-radio">
                                <input
                                    id="loop"
                                    v-model="item.radio"
                                    class="ui-radio"
                                    type="radio"
                                    value="0"
                                    :name="item.k" />
                                <label class="ui-label"
                                    for="loop"
                                    @click.stop="onAutoWaySwitch(index, '0')">
                                    {{ autoWay.loop.name }}
                                </label>
                            </div>
                            <div class="radio-item appoint-radio">
                                <input
                                    id="appoint"
                                    v-model="item.radio"
                                    class="ui-radio"
                                    type="radio"
                                    value="1"
                                    :name="item.k" />
                                <label class="ui-label"
                                    for="appoint"
                                    @click.stop="onAutoWaySwitch(index, '1')">
                                    {{ autoWay.appoint.name }}
                                </label>
                            </div>
                        </div>
                        <!-- 循环 -->
                        <div v-if="item.radio === '0'"
                            class="loop-select-bd">
                            {{ item.k !== 'week' ? autoWay.loop.start : autoWay.loop.start_week }}
                            <BaseInput
                                v-model.number="item.loop.start"
                                v-validate="item.loop.reg"
                                :name="item.k + 'Rule'"
                                class="loop-time"
                                @blur="renderRule()" />
                            {{ item.k !== 'week' ? item.title : ''}}{{ autoWay.loop.center }}
                            <BaseInput
                                v-model.number="item.loop.inter"
                                class="loop-time"
                                @blur="renderRule()" />
                            {{ item.k !== 'week' ? item.title : i18n.dayName }}{{ autoWay.loop.end }}
                            <!-- 说明 -->
                            <bk-tooltip v-if="item.k === 'week'" placement="left-end" class="month-tips">
                                <i class="common-icon-tooltips"></i>
                                <div slot="content">
                                    {{ i18n.monthTips }}
                                </div>
                            </bk-tooltip>
                            <div v-show="errors.has(item.k + 'Rule')" class="local-error-tip error-msg">{{ errors.first(item.k + 'Rule') }}</div>
                        </div>
                        <!-- 指定 -->
                        <div
                            v-else
                            class="appoint-select-bd">
                            <div v-for="(box, i) in item.checkboxList"
                                :key="i"
                                class="ui-checkbox-group">
                                <el-checkbox class="appoint-checkbox"
                                    v-model="box.checked"
                                    @change="renderRule">
                                    {{ box.value | add0(item.k) }}
                                </el-checkbox>
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
            <div v-else
                class="hand-input">
                <BaseInput
                    name="periodicCron"
                    class="step-form-content-size"
                    v-validate="periodicRule"
                    v-model="periodicCron"
                    :placeholder="i18n.placeholder" />
            </div>
        </div>
        <!-- 说明 -->
        <bk-tooltip placement="left-end" class="periodic-img-tooltip">
            <i class="common-icon-tooltips"></i>
            <div slot="content">
                <img :src="periodicCronImg" class="">
            </div>
        </bk-tooltip>
        <span v-show="errors.has('periodicCron')" class="common-error-tip error-msg">{{ errors.first('periodicCron') }}</span>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    // import { deepClone } from '@/utils/tools.js'
    import { PERIODIC_REG } from '@/constants/index.js'
    import BaseInput from '@/components/common/base/BaseInput.vue'
    const autoRuleList = [
        {
            k: 'min',
            title: gettext('分钟'),
            radio: '0',
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
            k: 'hour',
            title: gettext('小时'),
            radio: '0',
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
            k: 'week',
            title: gettext('星期'),
            radio: '0',
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
            k: 'day',
            title: gettext('日期'),
            radio: '0',
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
            k: 'month',
            title: gettext('月份'),
            radio: '0',
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
    const loopStar0List = ['min', 'hour', 'week']
    const loopStar1List = ['day', 'month']
    const autoWay = {
        'loop': {
            name: gettext('循环'),
            start: gettext('从第'),
            start_week: gettext('从星期'),
            center: gettext('开始,每隔'),
            end: gettext('执行')
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
            add0 (v, k) {
                return k === 'week' ? v : (v < 10 ? '0' + v : v)
            }
        },
        props: {
            manualInputValue: {
                type: String,
                default: ''
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
                    monthTips: gettext('0 表示新期天，6 表示星期六')
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
                return this.expressionList.join('^').replace(/\^/g, '~')
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
        mounted () {
        },
        methods: {
            onInputName () { },
            onInputBlur () { },
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
                this.$set(this.autoRuleList[index], 'radio', value)
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
                        const realityIndex = loopStar1List.includes(item.k) ? i + 1 : i
                        pushArr.push({
                            name: `${item.k}${i}`,
                            checked: true,
                            v: i,
                            value: item.k !== 'week' ? realityIndex : numberMap[realityIndex]
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
                    item.loop.start = loopStar0List.includes(item.k) ? 0 : 1
                    item.loop.inter = 1
                })
                this.renderRule()
            },
            /**
             *  渲染规则
             *  @param {String} key --tab key
             *  @param {String} way --自动/手动
             *  @param {Number} index --下标
             */
            renderRule (way = 'auto', index) {
                this.autoRuleList.map((m, i) => {
                    const { radio, loop, checkboxList, max } = m
                    const loopStr = loop.start === (loopStar0List.includes(m.k) ? 0 : 1) && loop.inter === 1
                        ? '*' : `${loop.start}-${max}/${loop.inter}`
                    const pointStr = checkboxList.filter(res => res.checked).map(res => {
                        // satrt 1 时 显示 i + 1
                        return loopStar1List.includes(m.k) ? res.v + 1 : res.v
                    }).join(',') || '*'
                    const data = radio === '0' ? loopStr : pointStr
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
                    return exportList.map(m => m.length > 1 ? `${m[0]}-${m[m.length - 1]}` : `${m[0]}`)
                } else {
                    return arr
                }
            },
            /**
             * 提交时验证表达式
             * @returns {Boolean} true/false
             */
            validationExpression () {
                autoRuleList.forEach(m => {
                    if (this.$validator.errors.has(m.k + 'Rule')) {
                        this.tabName = m.k
                        return false
                    }
                    return this.expressionShowText
                })
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
                            item.radio = '0'
                            item.checkboxList.forEach(t => {
                                t.checked = true
                            })
                        } else if (m.indexOf('/') !== -1 && m.split('/')[0].split('-')[1] * 1 === item.max) {
                            item.radio = '0'
                            item.loop.start = m.split('/')[0].split('-')[0] * 1
                            item.loop.inter = m.split('/')[1] * 1
                        } else if (m.indexOf('*/') !== -1) {
                            item.radio = '0'
                            item.loop.start = loopStar0List.includes(item.k) ? 0 : 1
                            item.loop.inter = m.split('/')[1] * 1
                        } else {
                            item.radio = '1'
                            item.checkboxList.forEach((box, boxIndex) => {
                                box.checked = m.split(',').some(s => {
                                    return loopStar1List.includes(item.k) ? s * 1 - 1 === box.v * 1 : s * 1 === box.v * 1
                                })
                            })
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
$colorBlue: #3A84FF;
$colorGrey: #63656e;

.ui-checkbox-group {
    display: inline-block;
    .appoint-checkbox{
        margin-right: 18px;
        margin-top: 20px;
        /deep/ .el-checkbox__label{
            color: $colorGrey;
        }
    }
}
.local-error-tip{
    margin-top: 10px;
    font-size: 14px;
    line-height: 1;
    color: #ff5757;
}
.loop-rule-select {
  position: relative;
  max-width: 500px;
  // 选择 title
  .loop-rule-title {
    .rule-btn {
      width: 50%;
      border: 1px solid $commonBorderColor;
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
        .loop-time{
            margin: 0 10px;
            width: 46px;
        }
        .month-tips{
            margin-left: 10px;
            color: #c4c6cc;
            font-size: 14px;
            &:hover {
            color: #f4aa1a;
            }
            /deep/ .bk-tooltip-arrow {
                display: none;
            }
        }
      }
      .appoint-select-bd {
        margin-top: 18px;
        padding: 0 20px 20px 20px;
        border: 1px solid $commonBorderColor;
      }
      .expression{
          margin-top: 20px;
          font-size: 14px;
          word-break: break-all;
          .clear-selected{
              margin-left: 20px;
              color: $colorBlue;
              cursor: pointer;
          }
      }
    }
  }
  .periodic-img-tooltip {
    position: absolute;
    right: -20px;
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
}
}
</style>
