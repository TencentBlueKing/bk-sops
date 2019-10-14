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
    <bk-tag-input
        v-model="setValue"
        :list="list"
        :placeholder="placeholder"
        :has-delete-icon="hasDeleteIcon"
        :max-data="maxData"
        :max-result="maxResult"
        save-key="username"
        search-key="username"
        display-key="username"
        @change="change"
        @select="select"
        @remove="remove">
    </bk-tag-input>
</template>
<script>
    import { errorHandler } from '@/utils/errorHandler.js'
    const BASE_URL = location.origin + window.MEMBER_URL
    export default {
        name: 'MemberSelector',
        model: {
            prop: 'value',
            event: 'change'
        },
        props: {
            /**
             * type
             * @description
             * all -人员和邮件组
             * rtx -人员
             * email -邮件组
             */
            type: {
                type: String,
                required: false,
                default: 'rtx'
            },
            value: {
                type: Array,
                required: false,
                default: () => []
            },
            placeholder: {
                type: String,
                required: false,
                default: ''
            },
            disabled: {
                type: Boolean,
                required: false,
                default: false
            },
            hasDeleteIcon: {
                type: Boolean,
                required: false,
                default: true
            },
            maxData: {
                type: Number,
                required: false,
                default: -1
            },
            maxResult: {
                type: Number,
                required: false,
                default: 5
            }
        },
        data () {
            return {
                list: []
            }
        },
        computed: {
            setValue: {
                get () {
                    return this.value
                },
                set (val) {
                    this.$emit('change', val)
                }
            }
        },
        created () {
            this.getRtxData()
            this.initData()
        },
        methods: {
            initData () {
                switch (this.type) {
                    case 'email':
                        this.getEmailData()
                        break
                    case 'all':
                        this.getAllData()
                        break
                    default:
                        this.getRtxData()
                }
            },
            change (tags) {
                this.$emit('change', tags)
            },
            select (tag) {
                this.$emit('select', tag)
            },
            remove (tag) {
                this.$emit('remove', tag)
            },
            getRtxData () {
                $.ajax({
                    url: BASE_URL,
                    methods: 'GET',
                    data: {
                        fields: 'username,id',
                        no_page: true
                    },
                    dataType: 'json',
                    success: res => {
                        if (res.result) {
                            this.list = Object.freeze(res.data)
                        } else {
                            errorHandler(res)
                        }
                    },
                    error: (err) => {
                        errorHandler(err)
                    }
                })
            },
            getEmailData () {

            },
            getAllData () {

            }
        }
    }
</script>
