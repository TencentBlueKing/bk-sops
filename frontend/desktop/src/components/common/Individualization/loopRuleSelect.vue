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
            <bk-tab
                v-if="currentWay === 'selectGeneration'"
                :type="'fill'" :size="'small'"
                :active-name="'min'"
                @tab-changed="tabChanged">
                <bk-tabpanel
                    v-for="(item, index) in autoRuleList"
                    :key="index"
                    :name="item.k"
                    :title="item.title">
                    <div class="tabpanel-container">
                        <div class="radio-group">
                            <div class="radio-item loop-radio">
                                <input
                                    class="ui-radio"
                                    type="radio"
                                    id="loop"
                                    v-model="item.radio"
                                    value="0"
                                    :name="item.k" />
                                <label
                                    class="ui-label"
                                    for="loop"
                                    @click.stop="onAutoWaySwitch(index, 0)">{{ autoWay.loop.name }}</label>
                            </div>
                            <div class="radio-item appoint-radio">
                                <input
                                    class="ui-radio"
                                    type="radio"
                                    id="appoint"
                                    v-model="item.radio"
                                    value="1"
                                    :name="item.k" />
                                <label
                                    class="ui-label"
                                    for="appoint"
                                    @click.stop="onAutoWaySwitch(index, 1)">{{ autoWay.appoint.name }}</label>
                            </div>
                        </div>
                        <div
                            v-if="item.radio === 0"
                            class="loop-select-bd">
                            111
                        </div>
                        <div
                            v-else
                            class="appoint-select-bd">
                            <div class="ui-checkbox-group">
                                <input
                                    type="checkbox"
                                    name="1"
                                    id="c1">
                                <label for="c1">01</label>
                            </div>
                        </div>
                    </div>
                </bk-tabpanel>
            </bk-tab>
            <!-- <div
                v-if="currentWay === 'selectGeneration'"
                class="auto-select-content">111</div> -->
            <div
                v-else
                class="hand-input">
                <BaseInput
                    ref="canvasNameInput"
                    :title="tName"
                    v-model="tName"
                    :placeholder="i18n.placeholder"
                    v-validate="templateNameRule"
                    data-vv-name="templateName"
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
    // import TagRadio from '@/components/common/RenderForm/tags/TagRadio.vue'
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
    export default {
        name: 'loopRuleSelect',
        components: {
            BaseInput
            // TagRadio
        },
        data () {
            return {
                i18n: {
                    error_code: gettext('错误码'),
                    placeholder: gettext('请输入 IP'),
                    selectGeneration: gettext('选择生成'),
                    manualInput: gettext('手动输入'),
                    TimeNavTex: []
                },
                autoRuleList: autoRuleList,
                autoWay: autoWay,
                currentWay: 'selectGeneration',
                currentRadio: 'loop',
                tName: '',
                templateNameRule: ''
            }
        },
        watch: {
        },
        mounted () { },
        methods: {
            onInputName () { },
            onInputBlur () { },
            onSwitchWay (way) {
                this.currentWay = way
            },
            tabChanged (e) {
                console.log(e, 'sssssssss')
            },
            onAutoWaySwitch (index, value) {
                const item = this.autoRuleList[index]
                item.radio = value
                this.$set(this.autoRuleList, index, item)
            }
        }
    }
</script>
<style lang="scss" scoped>
@import "@/scss/config.scss";
$blueBtnBg:#C7DCFF;
$colorBalck: #313238;
$colorGrey: #63656E;
.loop-rule-select {
  max-width: 500px;
  .loop-rule-title{
      .rule-btn{
          width: 50%;
          border: 1px solid $commonBorderColor;
      }
      .manual-input-btn{
          margin-left: -5px;
      }
      .active-btn{
          background-color: $blueBtnBg;
          border-color: $blueDefault;
          color: $blueDefault;
      }
  }
  .content-wrapper{
      margin-top: 18px;
      background-color: $whiteDefault;
      /deep/ .tab2-nav-item{
          width: 20%;
      }
      .tabpanel-container{
          padding: 20px;
          .radio-item{
              display: inline-block;
              &:not(:first-child){
                margin-left: 48px;
              }
              .ui-label{
                  font-size: 14px;
                  color: $colorGrey;
                  &::before{
                    content: "\a0"; /*不换行空格*/
                    display: inline-block;
                    vertical-align: middle;
                    width: 1em;
                    height: 1em;
                    margin-right: .4em;
                    border-radius: 50%;
                    border: 1px solid $commonBorderColor;
                    text-indent: .15em;
                    line-height: 1;
                    box-sizing: border-box;
                    font-size: 16px;
                  }
              }
              .ui-radio{
                  position: absolute;
                  clip: rect(0, 0, 0, 0);
              }
              .ui-radio:checked + .ui-label::before{
                    background-color: $blueDefault;
                    background-clip: content-box;
                    box-sizing: border-box;
                    padding: .2em;
              }
          }
          .loop-select-bd{
              margin-top: 18px;
              padding: 20px;
              border: 1px solid $commonBorderColor;
          }
          .appoint-select-bd{
              margin-top: 18px;
          }
      }
  }
}
</style>
