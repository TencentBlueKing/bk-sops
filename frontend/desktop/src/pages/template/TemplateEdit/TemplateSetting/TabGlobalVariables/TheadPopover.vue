<template>
    <bk-popover
        ref="popover"
        placement="bottom"
        theme="light"
        :distance="0"
        ext-cls="global-variable-popover"
        trigger="click"
        :on-show="handlePopoverShow"
        :on-hide="handlePopoverHide">
        <i :class="['bk-icon icon-funnel', { 'active': isShow || hasChecked }]"></i>
        <template slot="content">
            <ul class="content-list">
                <li
                    v-for="(item, index) in contentList"
                    :key="index"
                    class="content-item">
                    <bk-checkbox
                        :value="item.checked"
                        :disabled="item.code === 'all' ? false : isSelectedAll"
                        @change="onCheckChange($event, item)">
                    </bk-checkbox>
                    <span class="label-name" v-bk-overflow-tips>{{ item.name }}</span>
                </li>
            </ul>
            <div class="footer">
                <bk-button :text="true" title="primary" @click="handleConfirm">{{ $t('确定') }}</bk-button>
                <bk-button :text="true" title="primary" @click="handleReset">{{ $t('重置') }}</bk-button>
            </div>
        </template>
    </bk-popover>
</template>

<script>
    export default {
        props: {
            contentList: {
                type: Array,
                default: () => []
            },
            type: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                isShow: false,
                isSelectedAll: false
            }
        },
        computed: {
            hasChecked () {
                return this.contentList.some(item => item.checked)
            }
        },
        methods: {
            handlePopoverShow () {
                this.isShow = true
            },
            handlePopoverHide () {
                this.isShow = false
            },
            onCheckChange (e, info) {
                this.isSelectedAll = false
                if (info.code === 'all' && e) {
                    this.contentList.forEach(item => {
                        item.checked = false
                    })
                    this.isSelectedAll = true
                }
                info.checked = e
            },
            handleConfirm () {
                let checkedList = this.contentList.reduce((acc, cur) => {
                    if (cur.checked) {
                        acc.push(cur.code)
                    }
                    return acc
                }, [])
                checkedList = [...new Set(checkedList)]
                this.$emit('handleFilter', this.type, checkedList)
                this.$refs['popover'].hideHandler()
            },
            handleReset () {
                this.contentList.forEach(item => {
                    item.checked = false
                })
                this.isSelectedAll = false
                this.$emit('handleFilter', this.type, [])
                this.$refs['popover'].hideHandler()
            }
        }
    }
</script>

<style lang="scss">
@import '@/scss/mixins/scrollbar.scss';
.global-variable-popover {
    width: 147px;
    .tippy-tooltip {
        padding: 10px 0 0;
    }
    .content-list {
        max-height: 156px;
        padding: 0 10px;
        overflow-y: auto;
        @include scrollbar;
    }
    .content-item {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        .bk-form-checkbox {
            flex-shrink: 0;
            margin-right: 5px;
        }
        .label-name {
            flex: 1;
            font-size: 12px;
            color: #63656e;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
    }
    .footer {
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-top: 1px solid #f0f1f5;
        .bk-button-text {
            margin-right: 15px;
            font-size: 12px;
        }
    }
}
</style>
