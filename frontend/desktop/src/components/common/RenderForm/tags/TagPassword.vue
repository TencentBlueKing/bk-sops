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
    <div class="tag-password">
        <div v-if="formMode" class="password-edit-wrapper">
            <bk-select v-if="canUseVar" slot="prepend" class="select-type" :clearable="false" :value="localVal.tag" @selected="handleSelectType">
                <bk-option id="value" :name="$t('password_手动输入')"></bk-option>
                <bk-option id="variable" :name="$t('password_使用密码变量')"></bk-option>
            </bk-select>
            <template v-if="localVal.tag === 'value'">
                <input
                    v-if="!textareaMode"
                    class="value-input"
                    type="password"
                    :value="inputText"
                    :placeholder="inputPlaceholder"
                    @input="handleInput"
                    @focus="handleFocus"
                    @blur="handleBlur" />
                <textarea
                    v-else
                    class="value-textarea"
                    type="textarea"
                    rows="4"
                    :value="inputText"
                    :placeholder="inputPlaceholder"
                    @keydown="handleTextareaKeyDown"
                    @input="handleTextareaInput"
                    @keyup="handleTextareaKeyUp"
                    @focus="handleFocus"
                    @blur="handleBlur">
                </textarea>
            </template>
            <bk-select v-else class="select-var" :value="localVal.value" @selected="handleSelectVariable">
                <bk-option v-for="item in variables" :key="item.id" :id="item.id" :name="item.name"></bk-option>
            </bk-select>
            <span v-show="!validateInfo.valid" class="common-error-tip error-info">{{validateInfo.message}}</span>
        </div>
        <span v-else class="rf-view-value">{{(value.password === 'undefined' || value.password === '') ? '--' : '******'}}</span>
    </div>
</template>
<script>
    import cryptoJsSdk from '@blueking/crypto-js-sdk'
    import '@/utils/i18n.js'
    import i18n from '@/config/i18n/index.js'
    import EncryptRSA from '@/utils/encryptRSA.js'
    import { getFormMixins } from '../formMixins.js'

    export const attrs = {
        pubKey: {
            type: String,
            required: false,
            default: ''
        },
        canUseVar: {
            type: Boolean,
            required: false,
            default: true
        },
        textareaMode: {
            type: Boolean,
            required: false,
            default: false
        },
        disabled: {
            type: Boolean,
            required: false,
            default: false,
            desc: i18n.t('禁用组件')
        },
        value: {
            type: [String, Object],
            required: false,
            default: ''
        }
    }

    export default {
        name: 'TagPassword',
        mixins: [getFormMixins(attrs)],
        data () {
            return {
                localVal: {
                    tag: 'value',
                    value: ''
                },
                cursorPos: 0,
                inputText: '',
                inputPlaceholder: '',
                ASYMMETRIC_CIPHER_TYPE: window.ASYMMETRIC_CIPHER_TYPE,
                ASYMMETRIC_PUBLIC_KEY: window.ASYMMETRIC_PUBLIC_KEY,
                ASYMMETRIC_PREFIX: window.ASYMMETRIC_PREFIX
            }
        },
        computed: {
            variables () {
                const constants = $.context.getConstants() || {}
                return Object.keys(constants).filter(key => {
                    const item = constants[key]
                    return item.custom_type === 'password' && key !== this.tagCode
                }).map(key => {
                    const item = constants[key]
                    return { id: key, name: item.name }
                })
            }
        },
        watch: {
            value: {
                handler (val) {
                    if (Object.prototype.toString.call(val) === '[object Object]') {
                        this.localVal = { ...val }
                    } else {
                        this.localVal = {
                            tag: 'value',
                            value: val
                        }
                    }
                },
                immediate: true
            }
        },
        mounted () {
            if (this.localVal?.tag === 'value') {
                this.inputText = this.localVal.value ? '******' : ''
            }
        },
        methods: {
            handleSelectType (val) {
                this.localVal = {
                    tag: val,
                    value: ''
                }
                this.inputText = ''
                this.change()
            },
            handleInput (e) {
                this.localVal.value = e.target.value
                this.inputPlaceholder = ''
            },
            handleTextareaKeyDown (e) {
                this.cursorPos = e.target.selectionStart
            },
            handleTextareaInput (e) {
                const value = e.target.value
                const start = this.cursorPos > e.target.selectionStart ? e.target.selectionStart : this.cursorPos
                const crtLength = this.localVal.value.length
                const targetLength = value.length
                const lenGap = targetLength - crtLength
                if (lenGap < 0) { // 删除
                    this.localVal.value = this.localVal.value.slice(0, start) + this.localVal.value.slice(start - lenGap)
                } else { // 新增
                    this.localVal.value = this.localVal.value.slice(0, start) + value.slice(start, start + lenGap) + this.localVal.value.slice(start)
                }
            },
            handleTextareaKeyUp (e) {
                this.inputPlaceholder = ''
                this.inputText = e.target.value.replace(/[^\n]/g, '·')
            },
            handleFocus () {
                if (this.localVal.value.length > 0) {
                    this.inputPlaceholder = i18n.t('要修改密码请点击后重新输入密码')
                }
                this.localVal.value = ''
                this.inputText = ''
                this.change()
            },
            // 输入框失焦后执行加密逻辑
            handleBlur () {
                this.inputText = this.textareaMode ? this.localVal.value.replace(/[^\n]/g, '·') : this.localVal.value
                const encryptedVal = this.encryptPassword()
                this.localVal.value = encryptedVal
                this.change()
            },
            handleSelectVariable (val) {
                this.localVal.value = val
                this.change()
            },
            encryptPassword () {
                if (!this.localVal.value) {
                    return ''
                }
                const pubKey = this.pubKey || this.ASYMMETRIC_PUBLIC_KEY
                if (this.ASYMMETRIC_CIPHER_TYPE === 'RSA') {
                    const crypt = new EncryptRSA()
                    crypt.setPublicKey(pubKey)
                    const encryptedStr = crypt.encryptChunk(this.localVal.value)
                    return `${this.ASYMMETRIC_PREFIX}${encryptedStr}`
                } else {
                    const sm2 = new cryptoJsSdk.SM2()
                    const pkey = cryptoJsSdk.helper.asn1.decode(pubKey)
                    const cipher = sm2.encrypt(pkey, cryptoJsSdk.helper.encode.strToHex(this.localVal.value))
                    const base64Ret = cryptoJsSdk.helper.encode.hexToBase64(cipher)
                    return `${this.ASYMMETRIC_PREFIX}${base64Ret}`
                }
            },
            change () {
                this.$emit('change', [this.tagCode], this.localVal)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .password-edit-wrapper {
        display: flex;
        align-items: flex-start;
        .select-type {
            flex: 0 0 120px;
            border-right: none;
            border-top-right-radius: 0;
            border-bottom-right-radius: 0;
        }
        .value-input {
            flex: 1;
            padding: 0 10px;
            width: 100%;
            height: 32px;
            line-height: 32px;
            color: #63656e;
            background-color: #fff;
            border-top-right-radius: 2px;
            border-bottom-right-radius: 2px;
            font-size: 12px;
            border: 1px solid #c4c6cc;
            vertical-align: middle;
            text-align: left;
            outline: none;
            resize: none;
            &:focus {
                border-color: #3a84ff;
                background-color: #ffffff;
            }
        }
        .value-textarea {
            flex: 1;
            padding: 6px 10px;
            width: 100%;
            line-height: 16px;
            color: #63656e;
            background-color: #fff;
            border-top-right-radius: 2px;
            border-bottom-right-radius: 2px;
            font-size: 12px;
            border: 1px solid #c4c6cc;
            text-align: left;
            outline: none;
            resize: none;
            &:focus {
                border-color: #3a84ff;
                background-color: #ffffff;
            }
        }
        .select-var {
            flex: 1;
            border-top-left-radius: 0;
            border-bottom-left-radius: 0;
        }
        .bk-select {
            height: 32px;
        }
    }
</style>
