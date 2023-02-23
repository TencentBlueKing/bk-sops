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
    <div class="edit-scheme-wrap">
        <transition name="vertical-move">
            <div v-show="errorMsg" class="error-tips">{{ errorMsg }}</div>
        </transition>
        <div class="form-content">
            <bk-form form-type="vertical">
                <bk-form-item :label="$t('方案内容')" :required="true">
                    <bk-input type="textarea" :rows="16" v-model="schemeText" @paste="handleInputPaste" @blur="updateSelected"></bk-input>
                    <div class="content-tips">{{ $t('参考格式：步骤：节点名 标识位(0：不选择；1：选择；2：非可选节点)，并以换行符分隔。') }}</div>
                </bk-form-item>
                <bk-form-item :label="$t('变更节点对比')">
                    <bk-table :data="orderedNodeData">
                        <bk-table-column show-overflow-tooltip :label="$t('步骤名称')">
                            <template slot-scope="props">
                                {{ props.row.stage_name || '--' }}
                            </template>
                        </bk-table-column>
                        <bk-table-column show-overflow-tooltip :label="$t('节点名称')" prop="name"></bk-table-column>
                        <bk-table-column show-overflow-tooltip :label="$t('选中状态')">
                            <template slot-scope="props">
                                <span v-if="props.row.optional && excludeNodes.includes(props.row.id)" class="unselect">{{ $t('否') }}</span>
                                <span v-else>{{ $t('是') }}</span>
                            </template>
                        </bk-table-column>
                    </bk-table>
                </bk-form-item>
            </bk-form>
        </div>
        <div class="btn-wrap">
            <bk-button theme="primary" @click="onSaveScheme">{{ $t('保存') }}</bk-button>
            <bk-button @click="$emit('update:isShow', false)">{{ $t('取消') }}</bk-button>
        </div>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'

    export default {
        name: 'EditScheme',
        props: {
            orderedNodeData: Array
        },
        data () {
            const orderedNodeData = this.transformToText(this.orderedNodeData)
            return {
                excludeNodes: [],
                schemeText: orderedNodeData,
                initSchemeText: orderedNodeData,
                errorMsg: ''
            }
        },
        methods: {
            transformToText (nodes, excludeNodes = []) {
                let text = ''
                nodes.forEach(item => {
                    const { stage_name, name, optional } = item
                    const status = optional ? (excludeNodes.includes(item.id) ? 0 : 1) : 2
                    text += `${stage_name === '' ? '' : stage_name + '：'}${name} ${status}\n`
                })
                return text
            },
            judgeDataEqual () {
                return this.initSchemeText.trim() === this.schemeText.trim()
            },
            // 文本框粘贴
            handleInputPaste (value, event) {
                event.preventDefault()
                let paste = (event.clipboardData || window.clipboardData).getData('text')
                paste = paste.replace(/\\(t|s)/g, ' ')
                const selection = window.getSelection()
                if (!selection.rangeCount) return false
                if (selection.toString()) {
                    this.schemeText = value.replace(selection.toString(), paste)
                } else {
                    this.schemeText = value + paste
                }
            },
            updateSelected () {
                this.errorMsg = ''
                const text = this.schemeText.trim()
                const excludeNodes = []
                const passedNodes = [] // 匹配过的节点
                const rules = text.split('\n').filter(item => item.trim() !== '')
                if (rules.length !== this.orderedNodeData.length) {
                    this.errorMsg = i18n.t('方案节点个数（') + rules.length + i18n.t('）与实际节点个数（') + this.orderedNodeData.length + i18n.t('）不一致，请确认导出方案后模板是否有过修改')
                } else {
                    rules.some(textItem => {
                        if (textItem.trim() === '') {
                            return
                        }
                        let stageName = ''
                        let nodeName = ''
                        const stageSlice = textItem.split('：').filter(item => item.trim() !== '')
                        let nameSlice = ''

                        if (stageSlice.length > 1) {
                            stageName = stageSlice[0]
                            stageSlice.splice(0, 1)
                            nameSlice = stageSlice.join('：').split(' ').filter(item => item.trim() !== '')
                        } else {
                            stageName = ''
                            nameSlice = stageSlice[0].split(' ').filter(item => item.trim() !== '')
                        }

                        if (nameSlice.length > 1) {
                            const ind = nameSlice.length - 1
                            const statusText = Number(nameSlice[ind])
                            nameSlice.pop(ind)
                            nodeName = nameSlice.join(' ')
                            // 找到节点名称和步骤名称的节点并去掉已匹配的节点
                            const node = this.orderedNodeData.find(item => item.stage_name === stageName && item.name === nodeName && !passedNodes.includes(item.id))
                            if (node) {
                                passedNodes.push(node.id)
                                if (node.optional ? [0, 1].includes(statusText) : statusText === 2) {
                                    if (node.optional && statusText === 0) {
                                        excludeNodes.push(node.id)
                                    }
                                } else {
                                    this.errorMsg = i18n.t('方案中的（') + nodeName + i18n.t('）节点选择标记与模板中不一致，请确认导出方案后模板中节点可选配置是否有过修改')
                                    return true
                                }
                            } else {
                                this.errorMsg = i18n.t('方案中的（') + nodeName + i18n.t('）节点在模板中未找到，请确认导出方案后模板是否有过修改')
                                return true
                            }
                        } else {
                            const node = this.orderedNodeData.find(item => item.stage_name === stageName && item.name === nameSlice[0])
                            if (node) {
                                this.errorMsg = i18n.t('方案中的（') + nameSlice[0] + i18n.t('）节点选择标记与模板中不一致，请确认导出方案后模板中节点可选配置是否有过修改')
                            } else {
                                this.errorMsg = i18n.t('方案中的（') + nameSlice[0] + i18n.t('）节点在模板中未找到，请确认导出方案后模板是否有过修改')
                            }
                            return true
                        }
                    })

                    if (this.errorMsg === '') {
                        this.excludeNodes = excludeNodes
                    }
                }
            },
            onSaveScheme () {
                this.updateSelected()
                if (!this.errorMsg) {
                    const selectedNodes = this.orderedNodeData.filter(item => !this.excludeNodes.includes(item.id)).map(item => item.id)
                    this.$emit('importTextScheme', selectedNodes)
                    this.$emit('update:isShow', false)
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .edit-scheme-wrap {
        position: relative;
    }
    .error-tips {
        position: absolute;
        top: 0;
        left: 0;
        padding: 10px 15px;
        width: 100%;
        max-height: 66px;
        font-size: 12px;
        background: #fff4e2;
        border: 1px solid #ffdfac;
        box-shadow: 0px 2px 4px 0px #ede6db;
        color: #63656e;
        z-index: 10;
        overflow: auto;
    }
    .form-content {
        padding: 20px 20px 20px 40px;
        height: calc(100vh - 110px);
        overflow: auto;
        .content-tips {
            font-size: 12px;
            color: #63656e;
        }
    }
    .unselect {
        color: #ea3636;
    }
    .btn-wrap {
        padding: 8px 20px;
        border-top: 1px solid #cacedb;
    }
    .vertical-move-enter,
    .vertical-move-leave-to {
        opacity: 0;
        margin-top: -50px;
    }
    .vertical-move-enter-active,
    .vertical-move-leava-active {
        transition: margin .2s linear;
    }
</style>
