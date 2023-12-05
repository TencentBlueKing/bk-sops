<template>
    <bk-dialog
        ext-cls="cancel-global-variable-dialog"
        :show-mask="true"
        :mask-close="false"
        :show-footer="false"
        :value="isShow"
        @cancel="onCloseDialog">
        <template slot="header">
            <i class="bk-icon icon-exclamation"></i>
            <p class="title">{{ $t('无法取消使用变量') }}</p>
        </template>
        <p class="sub-title">{{ $t('变量已被引用，无法取消使用。如需取消，请先清除所有引用') }}</p>
        <bk-button theme="primary" @click="onViewCited">{{ $t('查看引用') }}</bk-button>
    </bk-dialog>
</template>

<script>
    export default {
        name: '',
        props: {
            isShow: Boolean
        },
        data () {
            return {
                
            }
        },
        methods: {
            onCloseDialog () {
                this.$parent.unhookingVar = ''
            },
            onViewCited () {
                this.$emit('onViewCited', {
                    group: 'activities',
                    id: this.$parent.unhookingVar
                })
                this.onCloseDialog()
            }
        }
    }
</script>

<style lang="scss">
.cancel-global-variable-dialog {
    .bk-dialog-header {
        padding: 0;
        margin-top: -3px;
        .icon-exclamation {
            display: inline-block;
            width: 42px;
            height: 42px;
            line-height: 42px;
            background-color: #ffe8c3;
            color: #ff9c01;
            font-size: 26px;
            border-radius: 50%;
        }
        .title {
            margin: 19px 0 8px;
            font-size: 20px;
            color: #313238;
            font-weight: normal;
        }
    }
    .bk-dialog-body {
        padding-bottom: 24px;
        text-align: center;
        .sub-title {
            color: #63656e;
            line-height: 22px;
            margin-bottom: 24px;
        }
    }
}
</style>
