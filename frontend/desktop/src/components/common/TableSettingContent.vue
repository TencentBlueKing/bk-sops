<template>
    <div class="bk-table-setting-content">
        <h2 class="content-title">{{ $t('表格设置') }}</h2>
        <div class="content-scroller">
            <div class="content-fields clearfix">
                <p class="setting-title">
                    {{ $t('字段显示设置') }}
                    <span class="setting-subtitle"
                        v-if="limit"
                        :class="{ 'is-limit': reachLimit }">
                        {{ $t('（最多{max}项）', { max: limit }) }}
                    </span>
                    <bk-checkbox class="fr setting-checkbox" v-else
                        :checked="allSelected"
                        @click.native="handleSelectAll">
                        {{ $t('全选') }}
                    </bk-checkbox>
                </p>
                <bk-checkbox-group v-model="localSelected" class="fields-group">
                    <template v-for="field in fields">
                        <span class="fields-checkbox-wrapper" :key="field[valueKey]">
                            <bk-checkbox class="fields-checkbox"
                                :disabled="field.hasOwnProperty('disabled') ? !!field.disabled : false"
                                :value="field[valueKey]"
                                :title="field[labelKey]">
                                {{field[labelKey]}}
                            </bk-checkbox>
                        </span>
                    </template>
                </bk-checkbox-group>
            </div>
            <div class="content-line-height">
                <p class="setting-title">
                    {{ $t('表格行高') }}
                </p>
                <div class="bk-button-group link-button-group">
                    <bk-button
                        size="small"
                        :class="['link-button', { 'is-selected': currentSize === 'small' }]"
                        @click="setSize('small')">
                        {{ $t('小') }}
                    </bk-button>
                    <bk-button
                        size="small"
                        :class="['link-button', { 'is-selected': currentSize === 'medium' }]"
                        @click="setSize('medium')">
                        {{ $t('中') }}
                    </bk-button>
                    <bk-button
                        size="small"
                        :class="['link-button', { 'is-selected': currentSize === 'large' }]"
                        @click="setSize('large')">
                        {{ $t('大') }}
                    </bk-button>
                </div>
            </div>
            <div class="order-setting">
                <p class="setting-title">
                    {{ $t('默认排序表头设置') }}
                </p>
                <bk-radio-group :value="localOrder.replace(/^-/, '')" @change="onOrderKeyChange">
                    <bk-radio v-for="(item, index) in sortableCols" class="field-radio-item" :key="index" :value="item.value">
                        <div class="label-wrapper">
                            <span style="margin-right: 8px;">{{ item.name }}</span>
                            <template v-if="localOrder.replace(/^-/, '') === item.value">
                                <span class="caret-area" style="margin-right: 4px;">
                                    <i :class="['triangle-icon', 'descending-icon', { active: /^-/.test(localOrder) }]"></i>
                                    <i :class="['triangle-icon', 'ascending-icon', { active: !/^-/.test(localOrder) }]"></i>
                                </span>
                                <span style="margin-right: 4px;">{{ $t('（') }}{{ localOrder === item.value ? $t('默认升序') : $t('默认降序') }}</span>
                                <span style="color: #3a84ff;" @click.stop="toggleOrderType(item.value)">{{ $t('切换') }}</span>
                                <span>{{ $t('）') }}</span>
                            </template>
                        </div>
                    </bk-radio>
                </bk-radio-group>
            </div>
        </div>
        <div class="content-options">
            <bk-button class="mr10" theme="primary"
                :disabled="reachLimit"
                @click="handleConfirm">
                {{ $t('确认') }}
            </bk-button>
            <bk-button theme="default" @click="handleCancel">{{ $t('取消') }}</bk-button>
        </div>
    </div>
</template>
<script>
    export default {
        name: 'TableSettingContent',
        props: {
            fields: {
                type: Array,
                default: () => ([])
            },
            selected: {
                type: Array,
                default: () => ([])
            },
            valueKey: {
                type: String,
                default: 'id'
            },
            labelKey: {
                type: String,
                default: 'label'
            },
            size: {
                type: String,
                default: 'small'
            },
            sortableCols: {
                type: Array,
                default: () => []
            },
            order: String,
            limit: Number
        },
        data () {
            return {
                localSelected: [],
                localOrder: this.order || '-id',
                currentSize: 'small'
            }
        },
        computed: {
            fieldsState () {
                const disabled = []
                const available = []
                const fixed = []
                this.fields.forEach(field => {
                    if (field.disabled) {
                        disabled.push(field)
                        if (this.localSelected.includes(field[this.valueKey])) {
                            fixed.push(field)
                        }
                    } else {
                        available.push(field)
                    }
                })
                return {
                    disabled,
                    available,
                    fixed
                }
            },
            disabledFields () {
                return this.fieldsState.disabled
            },
            availableFields () {
                return this.fieldsState.available
            },
            fixedFields () {
                return this.fieldsState.fixed
            },
            allSelected () {
                return this.availableFields.every(field => this.localSelected.includes(field[this.valueKey]))
            },
            reachLimit () {
                return this.limit && this.localSelected.length > this.limit
            },
            popoverInstance () {
                return this.$parent.instance
            }
        },
        watch: {
            selected: {
                immediate: true,
                handler (value) {
                    this.setSelected()
                }
            },
            size: {
                immediate: true,
                handler (size) {
                    this.setSize(size)
                }
            },
            order (val) {
                this.localOrder = val || '-id'
            },
            popoverInstance () {
                this.initCallback()
            }
        },
        methods: {
            initCallback () {
                this.popoverInstance.set({
                    onHidden: () => {
                        if (this.isConfirm) {
                            this.$emit('setting-change', {
                                fields: this.fields.filter(field => this.localSelected.includes(field[this.valueKey])),
                                size: this.currentSize,
                                order: this.localOrder
                            })
                        } else {
                            this.$emit('cancel')
                        }
                        this.isConfirm = false
                        this.$nextTick(() => {
                            this.setSelected()
                            this.setSize(this.size)
                        })
                    }
                })
            },
            setSelected () {
                this.localSelected = this.selected.map(field => field[this.valueKey])
            },
            setSize (size) {
                this.currentSize = size
            },
            handleSelectAll () {
                if (!this.allSelected) {
                    this.localSelected = this.fields.filter(field => this.fixedFields.includes(field) || !field.disabled).map(field => field[this.valueKey])
                } else {
                    this.localSelected = this.fixedFields.map(field => field[this.valueKey])
                }
            },
            onOrderKeyChange (id) {
                this.localOrder = id
            },
            toggleOrderType (id) {
                if (/^-/.test(this.localOrder)) {
                    this.localOrder = id
                } else {
                    this.localOrder = `-${id}`
                }
            },
            handleConfirm () {
                this.isConfirm = true
                this.popoverInstance.hide()
            },
            handleCancel () {
                this.isConfirm = false
                this.popoverInstance.hide()
            }
        }
    }
</script>
<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';

.bk-table-setting-content {
    width: 400px;
    .content-scroller {
        max-height: 317px;
        overflow-y: auto;
        @include scrollbar;
    }
    .content-title {
        padding: 0 24px;
        margin: 0;
        line-height: 32px;
        font-size:16px;
        font-weight: normal;
        color: #313238;
    }
    .setting-title {
        font-size: 14px;
        padding: 0;
        margin: 0;
        .setting-subtitle {
            display: inline-block;
            color: #979BA5;
            font-size: 12px;
            text-indent: -8px;
            margin-left: 10px;
            &.is-limit {
                color: #FF5656;
            }
        }
    }
    .content-fields {
        margin: 10px 24px 0;
    }
    .fields-group {
        .fields-checkbox-wrapper {
            display: inline-block;
            width: calc(100% / 3 - 15px);
            margin: 10px 15px 0 0;
        }
        .fields-checkbox {
            max-width: 100%;
            .bk-checkbox-text {
                display: inline-block;
                max-width: calc(100% - 22px);
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
        }
    }
    .content-line-height {
        margin: 25px 24px 0;
        .link-button-group {
            margin-top: 10px;
            font-size: 0;
        }
        .link-button {
            min-width: auto;
        }
    }
    .order-setting {
        margin: 25px 24px 0;
        .field-radio-item {
            display: block;
            margin: 10px 0;
        }
        .label-wrapper {
            display: inline-flex;
            align-items: center;
        }
        .caret-area {
            position: relative;
            display: inline-block;
            width: 10px;
            height: 20px;
            .triangle-icon  {
                position: absolute;
                left: 0;
                width: 0;
                height: 0;
                border: 5px solid transparent;
            }
            .ascending-icon {
                border-bottom-color: #c0c4cc;
                top: -1px;
                &.active {
                    border-bottom-color: #63656e;
                }
            }
            .descending-icon {
                border-top-color: #c0c4cc;
                bottom: -1px;
                &.active {
                    border-top-color: #63656e;
                }
            }
        }
    }
    .content-options {
        padding: 0 10px;
        margin: 30px 0 0;
        height: 51px;
        line-height: 50px;
        font-size: 0;
        text-align: right;
        background: #FAFBFD;
        border-top: 1px solid #DCDEE5;
    }
}
</style>
