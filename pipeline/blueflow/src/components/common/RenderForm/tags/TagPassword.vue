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
    <div class="tag-password">
        <div v-if="formMode">
            <el-input
                type="password"
                :disabled="!editable"
                :placeholder="i18n.placeholder"
                v-model="password"
                @focus="clearPassword"
                @blur="encryptPassword">
            </el-input>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="rf-view-value">{{(value.password === 'undefined' || value.password === '') ? '--' : passwordPlaceholder}}</span>
    </div>
</template>

<script>
import '@/utils/i18n.js'
import { mapState } from 'vuex'
import { getFormMixins } from '../formMixins.js'

const passwordAttrs = {
    value: {
        type: [String, Boolean],
        required: false,
        default: ''
    }
}
export default {
    name: "TagPassword",
    mixins: [getFormMixins(passwordAttrs)],
    data () {
        return {
            encrypted: false,
            passwordPlaceholder: '*****',
            i18n: {
                placeholder: gettext("要修改密码请点击后重新输入密码")
            }
        }
    },
    computed: {
        ...mapState({
            'rsa_pub_key': state => state.rsa_pub_key
        }),
        password: {
            get () {
                return this.encrypted ? this.tempValue : this.value
            },
            set (val) {
                this.tempValue = val
                this.updateForm(val)
            }
        }
    },
    methods: {
        _tag_init () {
            if (this.value) {
                this.encrypted = true
                this.tempValue = this.passwordPlaceholder
            }
        },
        clearPassword () {
            this.password = ''
            this.tempValue = ''
            this.encrypted = false
        },
        encryptPassword () {
            let val
            if (this.password === this.passwordPlaceholder) {
                return
            }
            if (this.password === '' || this.password === undefined) {
                val = ''
                return
            }
            var crypt = new JSEncrypt()
            crypt.setKey(this.rsa_pub_key)
            val = crypt.encrypt(this.password)
            
            this.encrypted = true
            this.tempValue = this.password
            this.$emit('change', [this.tagCode], val)
        }
    }
}
</script>

<style>
</style>
