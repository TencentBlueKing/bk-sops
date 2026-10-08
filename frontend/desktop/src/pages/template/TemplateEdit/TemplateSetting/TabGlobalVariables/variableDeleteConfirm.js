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
import i18n from '@/config/i18n/index.js'
import { mapState } from 'vuex'
import { getCitedGroups } from './citedUtils.js'

const DEFAULT_CITED_LIST = {
    activities: [],
    conditions: [],
    constants: []
}

/**
 * 变量删除二次确认弹窗（带引用范围提示）
 * 使用方式：this.openDeleteVariableConfirm(variables, confirmHandler)
 */
export default {
    computed: {
        ...mapState({
            'activities': state => state.template.activities,
            'lines': state => state.template.line,
            'gateways': state => state.template.gateways,
            'constants': state => state.template.constants,
            'internalVariable': state => state.template.internalVariable
        }),
        citedVariableList () {
            return { ...this.internalVariable, ...this.constants }
        }
    },
    methods: {
        /**
         * 获取变量引用详情分组
         * @param {Object} citedList 变量引用数据
         */
        getVariableCitedGroups (citedList) {
            return getCitedGroups(citedList, {
                activities: this.activities,
                lines: this.lines,
                gateways: this.gateways,
                variableList: this.citedVariableList
            })
        },
        /**
         * 生成单个变量的引用范围提示节点
         * @param {Function} h createElement
         * @param {Object} variable 变量数据
         * @param {Boolean} showKey 是否展示变量 key
         */
        getVariableCitedVNode (h, variable, showKey = false) {
            const citedList = (this.variableCited && this.variableCited[variable.key]) || DEFAULT_CITED_LIST
            const groups = this.getVariableCitedGroups(citedList)
            const total = groups.reduce((count, group) => count + group.data.length, 0)
            const children = []

            if (showKey) {
                children.push(h('div', { class: 'cited-confirm-key' }, [`【${variable.key}】`]))
            }

            if (!total) {
                children.push(h('div', { class: 'cited-confirm-empty' }, [i18n.t('该变量暂未被引用')]))
                return h('div', { class: 'cited-confirm-item' }, children)
            }

            children.push(h('div', { class: 'cited-confirm-summary' }, [
                i18n.t('该变量被引用'),
                h('span', { class: 'cited-danger' }, [String(total)]),
                i18n.t('处，删除后将导致以下引用失效：')
            ]))

            groups.forEach(group => {
                children.push(h('div', { class: 'cited-group' }, [
                    h('div', { class: 'cited-group-title' }, [
                        `${i18n.t('引用变量的')}${i18n.t(group.title)}`,
                        h('span', { class: 'cited-danger' }, [`（${group.data.length}）`])
                    ]),
                    h('div', { class: 'cited-group-list' }, group.data.map(item => h('div', {
                        class: 'cited-group-item',
                        on: {
                            click: () => this.onCitedItemClick(group.key, item.id)
                        }
                    }, [
                        h('span', { class: ['cited-group-name', { 'name-empty': !item.name }] }, [item.name || '--']),
                        h('i', { class: 'common-icon-box-top-right-corner' })
                    ])))
                ]))
            })

            return h('div', { class: 'cited-confirm-item' }, children)
        },
        /**
         * 打开删除变量的二次确认弹窗
         * @param {Array} variables 待删除的变量列表
         * @param {Function} confirmHandler 确认删除后的回调函数
         */
        openDeleteVariableConfirm (variables = [], confirmHandler) {
            if (!variables.length) {
                return
            }
            const h = this.$createElement
            const title = variables.length === 1
                ? i18n.t('确认删除') + i18n.t('全局变量') + `【${variables[0].key}】?`
                : i18n.t('确认删除所选的x个变量？', { num: variables.length })
            const multiVariable = variables.length > 1
            const citedVNodes = variables.map(variable => this.getVariableCitedVNode(h, variable, multiVariable))

            const infoInstance = this.$bkInfo({
                subHeader: h('div', { class: 'custom-header' }, [
                    h('div', {
                        class: 'custom-header-title',
                        directives: [{
                            name: 'bk-overflow-tips'
                        }]
                    }, [title]),
                    h('div', { class: 'custom-header-sub-title bk-dialog-header-inner' }, [
                        h('div', { class: 'delete-variable-tips' }, [i18n.t('删除变量将导致所有变量引用失效，请及时检查并更新节点配置')]),
                        h('div', { class: 'variable-cited-confirm' }, citedVNodes)
                    ])
                ]),
                extCls: 'dialog-custom-header-title',
                maskClose: false,
                width: 640,
                confirmLoading: true,
                cancelText: this.$t('取消'),
                confirmFn: () => {
                    if (typeof confirmHandler === 'function') {
                        return confirmHandler()
                    }
                }
            })
            // 引用详情点击跳转时需要先关闭弹窗，此实例非响应式数据
            this.deleteConfirmInstance = infoInstance
        },
        /**
         * 引用详情点击，关闭弹窗并跳转到对应位置
         */
        onCitedItemClick (group, id) {
            const instance = this.deleteConfirmInstance
            if (instance) {
                instance.onClose()
                this.deleteConfirmInstance = null
            }
            this.handleCitedNodeClick({ group, id })
        },
        /**
         * 引用详情跳转处理，使用方可以覆盖此方法自定义跳转行为
         */
        handleCitedNodeClick (data) {
            this.$emit('onCitedNodeClick', data)
        }
    }
}
