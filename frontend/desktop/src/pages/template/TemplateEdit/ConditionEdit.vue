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
    <div :class="['condition-edit', { 'position-right-side': !isSettingPanelShow }]" @click.stop>
        <div class="condition-title">{{ i18n.conditionTitle }}</div>
        <div class="condition-form">
            <div class="form-item">
                <label class="lable">
                    {{ i18n.conditionName }}
                    <span class="required">*</span>
                </label>
                <bk-input
                    v-model="conditionName"
                    v-validate="conditionRule"
                    name="conditionName"
                    :clearable="true">
                </bk-input>
                <span v-show="errors.has('conditionName')" class="common-error-tip error-msg">{{ errors.first('conditionName') }}</span>
            </div>
            <div class="form-item">
                <label class="lable">
                    {{ i18n.expression }}
                    <span class="required">*</span>
                </label>
                <textarea
                    v-model="expression"
                    v-validate="expressionRule"
                    name="expression"
                    autocomplete="off"
                    placeholder=""
                    class="ui-textarea">
                </textarea>
                <span v-show="errors.has('expression')" class="common-error-tip error-msg">{{ errors.first('expression') }}</span>
            </div>
        </div>
    </div>
</template>

<script>
    import '@/utils/i18n.js'
    import dom from '@/utils/dom.js'
    export default {
        name: 'conditionEdit',
        props: ['isSettingPanelShow', 'isShowConditionEdit'],
        data () {
            return {
                i18n: {
                    conditionTitle: gettext('分支条件'),
                    conditionName: gettext('分支名称'),
                    expression: gettext('表达式')
                },
                conditionName: '',
                expression: '',
                conditionRule: {
                    required: true
                },
                expressionRule: {
                    required: true
                },
                conditionData: {}
            }
        },
        mounted () {
            document.body.addEventListener('click', this.handleeConditionEditlShow, false)
        },
        beforeDestroy () {
            document.body.removeEventListener('click', this.handleeConditionEditlShow, false)
        },
        methods: {
            updateConditionData (data) {
                this.conditionData = data
                this.conditionName = data.name
                this.expression = data.value
            },
            /**
             * 处理节点配置面板和全局变量面板之外的点击事件
             */
            handleeConditionEditlShow (e) {
                if (!this.isShowConditionEdit) {
                    return
                }
                const settingPanel = document.querySelector('.setting-area-wrap')
                const nodeConfig = document.querySelector('.condition-edit')
                if (settingPanel && this.isShowConditionEdit) {
                    if ((!dom.nodeContains(settingPanel, e.target)
                        && !dom.nodeContains(nodeConfig, e.target))
                    ) {
                        this.closeConditionEdit()
                    }
                }
            },
            closeConditionEdit () {
                const { id, nodeId, overlayId } = this.conditionData
                this.$emit('onCloseConditionEdit', {
                    id,
                    nodeId,
                    overlayId,
                    value: this.expression,
                    name: this.conditionName
                })
            },
            checkCurrentConditionData () {
                this.closeConditionEdit()
                return this.$validator.validateAll()
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/config.scss';
@import '@/scss/mixins/scrollbar.scss';
.condition-edit {
    position: absolute;
    top: 59px;
    right: 476px;
    padding: 20px;
    width: 420px;
    height: calc(100% - 50px);
    background: #ffffff;
    border-left: 1px solid #dddddd;
    -webkit-box-shadow: -4px 0 6px -4px rgba(0, 0, 0, .15);
    box-shadow: -4px 0 6px -4px rgba(0, 0, 0, .15);
    overflow-y: auto;
    z-index: 5;
    -webkit-transition: right 0.5s ease-in-out;
    transition: right 0.5s ease-in-out;
    &.position-right-side {
        right: 56px;
    }
    .condition-title {
        height: 35px;
        line-height: 35px;
        margin: 0px 20px;
        border-bottom: 1px solid #cacecb;
        font-size: 14px;
        font-weight:600;
        color:#313238;
    }
    .condition-form {
        .form-item {
            margin: 0 20px;
            margin-bottom: 20px;
            .lable {
                display: block;
                position: relative;
                line-height: 36px;
                color: #313238;
                font-size: 14px;
                .required {
                    color: #ff2602;
                    font-family: "SimSun";
                }
            }
            .ui-textarea {
                height: 80px;
                line-height: 1;
                color: #63656e;
                background-color: #fff;
                border-radius: 2px;
                width: 100%;
                font-size: 12px;
                box-sizing: border-box;
                border: 1px solid #c4c6cc;
                padding: 6px 10px;
                text-align: left;
                vertical-align: middle;
                outline: none;
                resize: none;
            }
        }
    }
}
</style>
