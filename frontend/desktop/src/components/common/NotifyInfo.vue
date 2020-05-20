<template>
    <transition>
        <div v-if="show" class="notify-info">
            <i class="bk-icon icon-exclamation-circle tips-icon"></i>
            <div class="content-area">
                <slot>
                    <div class="content" :title="content">{{ content }}</div>
                </slot>
            </div>
            <div class="button-area">
                <slot name="buttons">
                    <bk-button
                        :text="true"
                        size="small"
                        @click="onHide">
                        {{ $t('收起') }}
                    </bk-button>
                </slot>
            </div>
        </div>
    </transition>
</template>
<script>
    export default {
        name: 'NotifyInfo',
        props: {
            content: {
                type: String
            },
            show: {
                type: Boolean,
                default: true
            }
        },
        data () {
            return {
                visible: this.show
            }
        },
        watch: {
            show (val) {
                this.visible = val
            }
        },
        methods: {
            onHide () {
                this.$emit('update:show', false)
            }
        }
    }
</script>
<style lang="scss" scoped>
    .notify-info {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        padding: 6px 10px;
        background: #ffeded;
        border: 1px solid #ffdddd;
        border-radius: 2px;
    }
    .tips-icon {
        margin-right: 8px;
        font-size: 16px;
        color: #ff5656;
    }
    .content-area {
        flex-grow: 1;
        padding-right: 100px;
        color: #63656e;
        font-size: 12px;
        .content {
            width: 100%;
            white-space: nowrap;
            text-overflow: ellipsis;
            overflow: hidden;
        }
    }
    .button-area {
        float: right;
    }
    .v-enter-active, .v-leave-active {
        transition: opacity .3s;
    }
    .v-enter, .v-leave-to {
        opacity: 0;
    }
</style>
