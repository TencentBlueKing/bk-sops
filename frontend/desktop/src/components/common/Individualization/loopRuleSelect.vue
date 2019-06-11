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
            <div
                v-if="currentWay === 'selectGeneration'"
                class="auto-select-content">111</div>
            <div
                v-else
                class="hand-input">
                <BaseInput class=""
                    ref="canvasNameInput"
                    :title="tName"
                    v-model="tName"
                    :placeholder="i18n.placeholder"
                    v-validate="templateNameRule"
                    data-vv-name="templateName"
                    :name="'templateName'"
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
    export default {
        name: 'loopRuleSelect',
        components: {
            BaseInput
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
                currentWay: 'selectGeneration',
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
            }
        }
    }
</script>
<style lang="scss" scoped>
@import "@/scss/config.scss";
$blueBtnBg:#C7DCFF;
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
      border: 1px solid $commonBorderColor;
  }
}
</style>
