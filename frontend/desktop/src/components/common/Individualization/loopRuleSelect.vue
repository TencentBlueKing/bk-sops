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
                :active-name="'min'"
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
                            <div v-show="errors.has(item.k + 'Rule')" class="local-error-tip error-msg">{{ errors.first(item.k + 'Rule') }}</div>
                        </div>
                        <!-- 指定 -->
                        <div
                            v-else
                            class="appoint-select-bd">
                            <div v-for="(box, i) in item.checkboxList"
                                :key="i"
                                class="ui-checkbox-group">
                                <input
                                    v-model="box.checked"
                                    type="checkbox"
                                    :id="box.name"
                                    :name="box.name"
                                    @change="renderRule('auto', index)">
                                <label class="ui-checkbox"
                                    :for="box.name">
                                    <!-- {{i|add0}} -->
                                    {{ box.value }}
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
            <div v-else
                class="hand-input">
                <BaseInput
                    class="step-form-content-size"
                    name="periodicCron"
                    v-model="periodicCron"
                    v-validate="periodicRule" />
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
                    regex: /^[0-59]{1,2}$/
                }
            }
        },
        {
            k: 'hour',
            title: gettext('小时'),
            radio: '1',
            long: 24,
            max: 23,
            loop: {
                start: 0,
                inter: 1,
                reg: {
                    required: true,
                    regex: /^[0-23]{1,2}$/
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
                    regex: /^[0-6]{1,2}$/
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
                    regex: /^[1-31]{1,2}$/
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
                    regex: /^[1-12]{1,2}$/
                }
            }
        }
    ]
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
    const loopStar0List = ['min', 'hour', 'week']
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
            add0 (v) {
                return v < 10 ? '0' + v : v
            }
        },
        data () {
            return {
                i18n: {
                    error_code: gettext('错误码'),
                    placeholder: gettext('0 12 * 10-17 */11'),
                    selectGeneration: gettext('选择生成'),
                    manualInput: gettext('手动输入'),
                    expression: gettext('表达式：'),
                    clearSelected: gettext('清空已选'),
                    dayName: gettext('天')
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
                periodicCron: '',
                tName: '',
                templateNameRule: ''
            }
        },
        computed: {
            expressionShowText () {
                return this.expressionList.join('^').replace(/\^/g, '~')
            }
        },
        watch: {
        },
        created () {
            this.initializeAutoRuleListData()
            this.renderRule()
        },
        mounted () {
            // this.initializeAutoRuleListData()
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
                console.log(name, 'sssssssss')
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
                        pushArr.push({
                            name: `${item.k}${i}`,
                            checked: false,
                            v: i,
                            value: item.k !== 'week' ? (i < 10 ? `0${i}` : `${i}`) : numberMap[i]
                        })
                    }
                    this.$set(this.autoRuleList[index], 'checkboxList', pushArr)
                })
            },
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
                    const pointStr = checkboxList.filter(res => res.checked).map(res => res.v).join(',') || '*'
                    const data = radio === '0' ? loopStr : pointStr
                    this.$set(this.expressionList, i, data)
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
  position: relative;
  margin-right: 24px;
  margin-top: 20px;
  font-size: 14px;
  & > label {
    cursor: pointer;
    color: $colorGrey;
  }
  & > input {
    position: absolute;
    clip: rect(0, 0, 0, 0);
  }
  & > label::before {
    content: "\a0"; /*不换行空格*/
    display: inline-block;
    vertical-align: middle;
    width: 15px;
    height: 16px;
    margin-right: 8px;
    border: 1px solid $commonBorderColor;
    box-sizing: border-box;
  }
  & > input:checked + label::before {
    background-color: $blueDefault;
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
    /deep/ .active {
      border-bottom: none;
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
      }
      .appoint-select-bd {
        margin-top: 18px;
        padding: 0 20px 20px 20px;
        border: 1px solid $commonBorderColor;
      }
      .expression{
          margin-top: 20px;
          font-size: 14px;
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
