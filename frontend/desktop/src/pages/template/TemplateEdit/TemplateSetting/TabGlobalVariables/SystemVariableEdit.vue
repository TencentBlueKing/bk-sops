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
            <!-- 引用节点 -->
            <li class="form-item clearfix">
                <label class="form-label">{{ i18n.cited }}</label>
                <div class="form-content">
                    <bk-select
                        :clearable="false">
                        <bk-option
                            v-for="(option, index) in currConstantsCited"
                            :key="index"
                            :id="option.name"
                            :name="`${option.name}（${option.numbers}）`">
                        </bk-option>
                    </bk-select>
                </div>
            </li>
        </ul>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState } from 'vuex'
    export default {
        name: 'SystemVariableEdit',
        props: ['variableData'],
        data () {
            return {
                i18n: {
                    name: gettext('名称'),
                    desc: gettext('说明'),
                    cited: gettext('引用节点')
                },
                constantCitedList: ['name', 'fdsfdsfds']
            }
        },
        computed: {
            ...mapState({
                'constantsCited': state => state.template.constantsCited
            }),
            // 当前变量引用的节点信息
            currConstantsCited () {
                const cuurKey = this.variableData.key
                const nodes = []
                for (const node in this.constantsCited) {
                    for (const key in this.constantsCited[node]) {
                        if (cuurKey === key) {
                            nodes.push({
                                name: node,
                                numbers: this.constantsCited[node][key]
                            })
                        }
                    }
                }
                return nodes
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
    .bk-select {
        background: #ffffff;
    }
    input {
        padding: 0 10px;
        width: 100%;
        height: 36px;
        line-height: 36px;
        font-size: 14px;
        border: 1px solid $formBorderColor;
        border-radius: 2px;
        outline: none;
        &:focus {
            border-color: $blueDefault;
        }
        &[disabled] {
            color: #aaa;
            cursor: not-allowed;
            background: #fafafa;
        }
    }
    textarea {
        padding: 10px;
        width: 100%;
        height: 70px;
        border: 1px solid $formBorderColor;
        border-radius: 2px;
        outline: none;
        resize: none;
        &:hover {
            border-color: #c0c4cc;
        }
        &:focus {
            border-color: $blueDefault;
        }
        @include scrollbar;
    }
    /deep/ .el-input {
        .el-input__inner {
            padding: 0 10px;
            height: 36px;
            line-height: 36px;
        }
    }
    /deep/ .tag-form {
        margin-left: 0;
    }
}
</style>
