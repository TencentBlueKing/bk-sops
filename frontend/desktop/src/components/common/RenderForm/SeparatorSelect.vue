/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="separator-select">
        <bk-form>
            <bk-form-item :label="$t('分隔符：')" :label-width="70">
                <bk-radio-group :value="value" @change="onChange">
                    <bk-radio
                        v-for="option in options"
                        :key="option.value"
                        :disabled="!editable"
                        :value="option.value">
                        {{ option.label }}
                    </bk-radio>
                </bk-radio-group>
            </bk-form-item>
        </bk-form>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    export default {
        name: 'SeparatorSelect',
        model: {
            prop: 'value',
            event: 'change'
        },
        props: {
            editable: Boolean,
            value: [String, Boolean, Number],
            options: {
                type: Array,
                default () {
                    return [
                        { label: i18n.t('逗号'), value: ',' },
                        { label: i18n.t('分号'), value: ';' },
                        { label: i18n.t('竖线'), value: '|' },
                        { label: i18n.t('换行符'), value: '\n' }
                    ]
                }
            }
        },
        data () {
            return {
                localValue: this.value
            }
        },
        watch: {
            value (val) {
                this.localValue = val
            }
        },
        methods: {
            onChange (value) {
                this.$emit('change', value)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .separator-select {
        margin: 20px 0;
    }
    ::v-deep .bk-form-item {
        .bk-label {
            padding-right: 10px;
            font-size: 12px;
            text-align: left;
            color: #313238;
        }
        .bk-form-radio {
            margin-right: 30px;
            font-size: 12px;
            color: #313238;
        }
    }
</style>
