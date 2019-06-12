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
                                <input class="ui-radio"
                                    type="radio"
                                    id="loop"
                                    v-model="item.radio"
                                    value="0"
                                    :name="item.k" />
                                <label class="ui-label"
                                    for="loop"
                                    @click.stop="onAutoWaySwitch(index, '0')">
                                    {{ autoWay.loop.name }}
                                </label>
                            </div>
                            <div class="radio-item appoint-radio">
                                <input class="ui-radio"
                                    type="radio"
                                    id="appoint"
                                    v-model="item.radio"
                                    value="1"
                                    :name="item.k" />
                                <label class="ui-label"
                                    for="appoint"
                                    @click.stop="onAutoWaySwitch(index, '1')">
                                    {{ autoWay.appoint.name }}
                                </label>
                            </div>
                        </div>
                        <div v-if="item.radio === '0'"
                            class="loop-select-bd">
                            111
                        </div>
                        <div v-else
                            class="appoint-select-bd">
                            <div v-for="(box, i) in item.showTextList"
                                :key="i"
                                class="ui-checkbox-group">
                                <input type="checkbox"
                                    v-model="box.checked"
                                    :name="box.name"
                                    :id="box.name">
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
                                class="clear-selected">{{ i18n.clearSelected }}
                            </span>
                        </div>
                    </div>
                </bk-tabpanel>
            </bk-tab>
            <div v-else
                class="hand-input">
                <BaseInput ref="canvasNameInput"
                    v-model="tName"
                    data-vv-name="templateName"
                    v-validate="templateNameRule"
                    :title="tName"
                    :placeholder="i18n.placeholder"
                    :name="'ruleName'"
                    @input="onInputName"
                    @blur="onInputBlur"
                    @enter="onInputBlur">
                </BaseInput>
            </div>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import BaseInput from '@/components/common/base/BaseInput.vue'
    const autoRuleList = [
        {
            k: 'min',
            title: gettext('分钟'),
            radio: '1',
            long: 60
        },
        {
            k: 'hour',
            title: gettext('小时'),
            radio: '1',
            long: 24
        },
        {
            k: 'week',
            title: gettext('星期'),
            radio: '0',
            long: 7
        },
        {
            k: 'day',
            title: gettext('日期'),
            radio: '0',
            long: 31
        },
        {
            k: 'month',
            title: gettext('月份'),
            radio: '0',
            long: 12
        }
    ]
    const autoWay = {
        'loop': {
            name: gettext('循环'),
            start: gettext('从第'),
            center: gettext('开始,每隔'),
            end: gettext('执行')
        },
        'appoint': {
            name: gettext('指定')
        }
    }
    const numberMap = {
        0: gettext('星期一'),
        1: gettext('星期二'),
        2: gettext('星期三'),
        3: gettext('星期四'),
        4: gettext('星期五'),
        5: gettext('星期六'),
        6: gettext('星期天')
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
                    placeholder: gettext('请输入 IP'),
                    selectGeneration: gettext('选择生成'),
                    manualInput: gettext('手动输入'),
                    expression: gettext('表达式：'),
                    clearSelected: gettext('清空已选'),
                    TimeNavTex: []
                },
                expressionList: ['0', '*', '11', '522'],
                // 规则列表
                autoRuleList: autoRuleList,
                // 循环选择方式
                autoWay: autoWay,
                // manualInput 手动 / selectGeneration 选择生成
                currentWay: 'selectGeneration',
                currentRadio: 'loop',
                tName: '',
                templateNameRule: ''
            }
        },
        computed: {
            expressionShowText () {
                return this.expressionList.join(',').replace(/\,/g, ' ')
            }
        },
        watch: {
        },
        created () {
            // this.initializeAutoRuleListData()
        },
        mounted () {
            this.initializeAutoRuleListData()
        },
        methods: {
            onInputName () { },
            onInputBlur () { },
            onSwitchWay (way) {
                this.currentWay = way
            },
            tabChanged (e) {
                console.log(e, 'sssssssss')
            },
            /**
             * 周期循环方式切换,循环/指定
             * @param {Number} index - 下标
             * @param {Number} value - 改变的值
             */
            onAutoWaySwitch (index, value) {
                this.$set(this.autoRuleList[index], 'radio', value)
            },
            initializeAutoRuleListData () {
                this.autoRuleList.forEach((item, index) => {
                    const pushArr = []
                    for (let i = 0; i < item.long; i++) {
                        pushArr.push({
                            name: `${item.k}${i}`,
                            checked: false,
                            value: item.k !== 'week'
                                ? (i < 10 ? `0${i}`
                                    : `${i}`) : numberMap[i]
                        })
                    }
                    this.$set(this.autoRuleList[index], 'showTextList', pushArr)
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
.loop-rule-select {
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
        padding: 20px;
        border: 1px solid $commonBorderColor;
      }
      .appoint-select-bd {
        margin-top: 18px;
        padding: 0 20px 20px 20px;
        border: 1px solid $commonBorderColor;
      }
      .expression{
          margin-top: 18px;
          font-size: 14px;
          .clear-selected{
              margin-left: 20px;
              color: $colorBlue;
              cursor: pointer;
          }
      }
    }
  }
}
</style>
