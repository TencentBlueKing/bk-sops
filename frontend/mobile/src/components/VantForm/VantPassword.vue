/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
<template>
    <van-field
        type="password"
        name="parameterInput"
        :label="label"
        :placeholder="i18n.placeholder"
        :error="isError"
        :error-message="errors.first('parameterInput')"
        v-validate="validation"
        v-model="password"
        @focus="clearPassword" />
</template>

<script>

    export default {
        name: 'VantPassword',
        props: {
            label: {
                type: String,
                default: ''
            },
            placeholder: {
                type: String,
                default: ''
            },
            value: {
                type: String,
                default: ''
            },
            name: {
                type: String,
                default: ''
            },
            validation: {
                type: Object,
                default () {
                    return {}
                }
            }
        },
        data () {
            return {
                password: '',
                encrypted: true,
                passwordPlaceholder: '*****',
                i18n: {
                    placeholder: window.gettext('要修改密码请点击后重新输入密码')
                }
            }
        },
        computed: {
            isError () {
                return this.errors.has('parameterInput')
            }
        },
        mounted () {
            this.init()
        },
        methods: {
            init () {
                if (this.value) {
                    this.encrypted = true
                    this.password = this.passwordPlaceholder
                }
            },
            clearPassword () {
                this.password = ''
                this.encrypted = false
            }
        }

    }
</script>
