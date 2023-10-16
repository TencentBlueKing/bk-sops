<template>
    <div :class="[
        'variable-item',
        {
            'edit-model': !isViewMode,
            'is-active': showCitedList,
            'variable-animation': newCloneKeys.includes(variableData.key)
        }]">
        <section class="variable-wrap">
            <bk-checkbox
                v-if="!isViewMode"
                :disabled="isComponentVar || isInternalVal"
                :value="variableChecked"
                v-bk-tooltips="{ content: componentVarDisabledTip, disabled: !isComponentVar }"
                @change="onChooseVariable">
            </bk-checkbox>
            <div class="variable-content">
                <div class="variable-name">
                    <span v-bk-overflow-tips class="ellipsis">{{ variableData.name }}</span>
                    <span v-if="['component_outputs', 'project'].includes(variableData.source_type)" :class="variableData.source_type">
                        <i
                            v-if="variableData.source_type === 'component_outputs'"
                            class="common-icon-hide-right"
                            v-bk-tooltips="$t('作为输出参数')">
                        </i>
                        <i
                            v-if="variableData.source_type === 'project'"
                            class="common-icon-xiangmu"
                            v-bk-tooltips="$t('从项目变量添加')">
                        </i>
                    </span>
                    <span v-if="isSpecialModel" class="variable-type ellipsis" v-bk-overflow-tips>{{ variableData.type }}</span>
                </div>
                <div class="variable-key" v-bk-overflow-tips>
                    {{ variableData.key }}
                </div>
                <span v-if="!isSpecialModel" class="copy-icon">
                    <i
                        class="common-icon-copy"
                        v-bk-tooltips.bottom="{
                            content: $t('复制'),
                            placement: 'top',
                            boundary: 'window'
                        }"
                        @click.stop="onCopyKey(variableData.key)">
                    </i>
                </span>
                <div v-else-if="!isViewMode" class="variable-operate">
                    <i
                        class="common-icon-cited-link"
                        :class="{ 'active': showCitedList }"
                        v-bk-tooltips.bottom="{
                            content: $t('引用'),
                            placement: 'top',
                            boundary: 'window'
                        }"
                        @click.stop="onShowCitedList">
                        <span class="count">{{ citedNum }}</span>
                    </i>
                    <i
                        class="common-icon-copy"
                        v-bk-tooltips.bottom="{
                            content: $t('复制'),
                            placement: 'top',
                            boundary: 'window'
                        }"
                        @click.stop="onCopyKey(variableData.key)">
                    </i>
                    <bk-dropdown-menu :align="'right'" ext-cls="tpl-header-more-dropdown" :position-fixed="true" v-if="!isInternalVal">
                        <div slot="dropdown-trigger" class="dropdown-trigger">
                            <i class="bk-icon icon-more"></i>
                        </div>
                        <ul class="bk-dropdown-list" slot="dropdown-content">
                            <li
                                v-if="!isComponentVar"
                                class="dropdown-item"
                                @click="onCloneVariable">
                                {{ '克隆' }}
                            </li>
                            <li
                                :class="['dropdown-item', { 'disabled': isComponentVar }]"
                                v-bk-tooltips="{ content: $t('该类型仅支持从节点配置取消引用'), disabled: !isComponentVar }"
                                @click="onDeleteVariable">
                                {{ '删除' }}
                            </li>
                        </ul>
                    </bk-dropdown-menu>
                </div>
                
            </div>
        </section>
        <!--变量引用-->
        <VariableCitedList
            v-if="showCitedList"
            :cited-list="citedList"
            @onCitedNodeClick="$emit('onCitedNodeClick', $event)">
        </VariableCitedList>
    </div>
</template>

<script>
    import i18n from '@/config/i18n/index.js'
    import VariableCitedList from './VariableCitedList.vue'
    export default {
        name: 'VariableItem',
        components: {
            VariableCitedList
        },
        props: {
            variableData: Object,
            panelType: String,
            isViewMode: Boolean,
            newCloneKeys: Array,
            variableCited: Object,
            variableChecked: Boolean,
            internalVariable: [Object, Array]
        },
        data () {
            return {
                copyText: '',
                showCitedList: false
            }
        },
        computed: {
            isSpecialModel () {
                return this.panelType === 'detail'
            },
            isSystemVar () {
                return this.variableData.source_type === 'system'
            },
            isProjectVar () {
                return this.variableData.source_type === 'project'
            },
            // 是否为内置变量
            isInternalVal () {
                const keys = Object.keys(this.internalVariable)
                return keys.some(key => key === this.variableData.key)
            },
            isComponentVar () {
                return ['component_outputs', 'component_inputs'].includes(this.variableData.source_type)
            },
            componentVarDisabledTip () {
                return this.variableData.source_type === 'component_inputs'
                    ? i18n.t('节点输入型变量仅支持从节点"取消使用变量"来删除')
                    : i18n.t('节点输出型变量仅支持从节点"取消接收输出"来删除')
            },
            citedList () {
                const defaultCiteData = {
                    activities: [],
                    conditions: [],
                    constants: []
                }
                return this.variableCited[this.variableData.key] || defaultCiteData
            },
            citedNum () {
                const { activities, conditions, constants } = this.citedList
                return activities.length + conditions.length + constants.length
            }
        },
        methods: {
            /**
             * 变量 key 复制
             */
            onCopyKey (key) {
                this.copyText = key
                document.addEventListener('copy', this.copyHandler)
                document.execCommand('copy')
                document.removeEventListener('copy', this.copyHandler)
                this.copyText = ''
            },
            /**
             * 复制操作回调函数
             */
            copyHandler (e) {
                e.preventDefault()
                e.clipboardData.setData('text/html', this.copyText)
                e.clipboardData.setData('text/plain', this.copyText)
                this.$bkMessage({
                    message: 'key' + i18n.t('已复制'),
                    theme: 'success'
                })
            },
            onChooseVariable (value) {
                this.$emit('onChooseVariable', this.variableData, value)
            },
            onCloneVariable () {
                if (this.isComponentVar) return
                this.$emit('onCloneVariable', this.variableData)
            },
            onDeleteVariable () {
                if (this.isComponentVar) return
                const h = this.$createElement
                this.$bkInfo({
                    subHeader: h('div', { class: 'custom-header' }, [
                        h('div', {
                            class: 'custom-header-title',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('确认删除') + i18n.t('全局变量') + `【${this.variableData.key}】?`]),
                        h('div', {
                            class: 'custom-header-sub-title bk-dialog-header-inner',
                            directives: [{
                                name: 'bk-overflow-tips'
                            }]
                        }, [i18n.t('删除变量将导致所有变量引用失效，请及时检查并更新节点配置')])
                    ]),
                    extCls: 'dialog-custom-header-title',
                    maskClose: false,
                    width: 450,
                    confirmLoading: true,
                    cancelText: this.$t('取消'),
                    confirmFn: () => {
                        this.$emit('onDeleteVariable', this.variableData.key)
                    }
                })
            },
            onShowCitedList () {
                if (!this.citedNum) return
                this.showCitedList = !this.showCitedList
            }
        }
    }
</script>

<style lang="scss" scoped>
.variable-item {
    font-size: 12px;
    line-height: 20px;
    padding: 8px 12px;
    color: #63656e;
    border-bottom: 1px solid #dcdee5;
    cursor: pointer;
    .variable-wrap {
        display: flex;
        .bk-form-checkbox {
            flex-shrink: 0;
            margin-top: 12px;
            margin-right: 8px;
        }
    }
    .variable-content {
        position: relative;
        width: 100%;
    }
    .variable-name {
        display: flex;
        align-items: center;
        justify-content: space-between;
        .component_outputs,
        .project {
            flex: 1;
            flex-shrink: 0;
            height: 20px;
            text-align: left;
            margin-top: -8px;
            i {
                display: inline-block;
                font-size: 16px;
                transform: scale(0.5);
                padding: 6px;
                color: #fff;
                border-radius: 2px;
            }
        }
        .component_outputs i {
            background: #85cca8;
        }
        .project i {
            background: #61b2c2;
        }
        .variable-type {
            flex-shrink: 0;
            line-height: 22px;
            max-width: 120px;
            padding: 0 10px;
            color: #63656e;
            background: #eaebf0;
            border-radius: 2px;
        }
    }
    .variable-key {
        color: #979ba5;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    .copy-icon {
        position: absolute;
        right: 0;
        top: 0;
        display: none;
        padding-left: 8px;
        height: 100%;
        font-style: 14px;
        line-height: 40px;
        cursor: pointer;
        i {
            font-size: 14px;
            &:hover {
                color: #3a84ff;
            }
        }
    }
    .variable-operate {
        position: absolute;
        right: 0;
        bottom: 0;
        display: none;
        font-size: 16px;
        padding-left: 8px;
        color: #979ba5;
        .common-icon-copy {
            margin: 0 2px;
        }
        .count {
            font-size: 12px;
        }
        .tpl-header-more-dropdown {
            margin-bottom: 0;
            .dropdown-trigger {
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 16px;
                color: #979ba5;
                background: transparent;
                border-radius: 50%;
                cursor: pointer;
                &:hover {
                    color: #3a84ff;
                    background: rgba(49, 50, 56, 0.1);
                    
                }
            }
            .dropdown-item {
                display: flex;
                align-items: center;
                width: 58px;
                height: 32px;
                padding-left: 12px;
                font-size: 12px;
                color: #63656e;
                cursor: pointer;
                i {
                    color: #979ba5;
                    font-size: 14px;
                    margin-right: 4px;
                }
                &:hover {
                    background: #f5f7fa;
                    color: #3a84ff;
                    i {
                        color: #3a84ff;
                    }
                }
            }
        }
        .active,
        i:hover {
            color: #3a84ff;
        }
    }
    .ellipsis {
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    &.is-active,
    &:hover {
        background: #f0f1f5;
        .copy-icon {
            display: block;
            background: #f0f1f5;
        }
        .variable-operate {
            display: block;
            background: #f0f1f5;
        }
        .variable-type {
            background: #dcdee5;
        }
    }
}
.edit-model {
    padding-left: 8px;
    .bk-form-checkbox {
        margin-top: 16px;
    }
    .variable-content {
        width: calc(100% - 24px);;
    }
    .variable-name {
        margin: -2px 0 4px;
    }
}
.variable-animation {
    animation: bgAnimation 3.5s;
}
@keyframes bgAnimation {
    0%{ background: #f2fcf5; }
    85%{ background: #f2fcf5; }
    100%{ background: #fff; }
}
</style>
