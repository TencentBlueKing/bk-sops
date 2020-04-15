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
    <div>
        <div class="variable-operation-tips"> {{ varOperatingTips }} </div>
        <div class="variable-edit-wrapper" @click="e => e.stopPropagation()">
            <ul class="form-list">
                <!-- 名称 -->
                <li class="form-item clearfix">
                    <label class="required">{{ i18n.name }}</label>
                    <div class="form-content">
                        <bk-input
                            name="variableName"
                            :value="variableData.name"
                            :disabled="true">
                        </bk-input>
                    </div>
                </li>
                <!-- key -->
                <li class="form-item clearfix">
                    <label class="required">KEY</label>
                    <div class="form-content">
                        <bk-input
                            name="variableKey"
                            :value="variableData.key"
                            :disabled="true">
                        </bk-input>
                    </div>
                </li>
                <!-- 说明 -->
                <li class="form-item clearfix">
                    <label class="required">{{ i18n.desc }}</label>
                    <div class="form-content">
                        <bk-input
                            type="textarea"
                            :disabled="true"
                            :value="variableData.desc || ' '">
                        </bk-input>
                    </div>
                </li>
            </ul>
        </div>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    export default {
        name: 'SystemVariableEdit',
        props: ['variableData', 'varOperatingTips'],
        data () {
            return {
                i18n: {
                    name: gettext('名称'),
                    desc: gettext('说明'),
                    cited: gettext('引用节点')
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
$localBorderColor: #d8e2e7;
.variable-edit-wrapper {
    padding: 20px;
    padding-bottom: 40px;
    font-size: 14px;
    text-align: left;
    background: $whiteThinBg;
    border-bottom: 1px solid $localBorderColor;
    cursor: auto;
}
.variable-operation-tips {
    height: 43px;
    line-height: 43px;
    color: #63656e;
    font-size: 12px;
    text-align: center;
    background: #f0f1f5;
    border-top: 1px solid #dcdee5;
    border-bottom: 1px solid #dcdee5;
}
.error-msg {
    margin-top: 10px;
}
.form-item {
    margin: 15px 0;
    &:first-child {
        margin-top: 0;
    }
    label {
        position: relative;
        float: left;
        width: 60px;
        margin-top: 8px;
        font-size: 12px;
        color: $greyDefault;
        text-align: right;
        word-wrap: break-word;
        word-break: break-all;
        &.required:before {
            content: '*';
            position: absolute;
            top: 0px;
            right: -10px;
            color: $redDark;
            font-family: "SimSun";
        }
    }
}
.form-content {
    margin-left: 80px;
    min-height: 36px;
    /deep/ .bk-textarea-wrapper {
        border: none;
    }
    /deep/ .bk-form-textarea {
        border: 1px solid #c4c6cc;
    }
}
</style>
