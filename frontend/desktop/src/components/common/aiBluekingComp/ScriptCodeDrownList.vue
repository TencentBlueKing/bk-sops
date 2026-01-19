<template>
    <bk-dropdown-menu>
        <template slot="dropdown-trigger">
            <img
                src="@/assets/images/assistant-small.svg"
                class="assistant-icon mr20"
                alt="assistant"
            />
        </template>
        <template slot="dropdown-content">
            <ul class="bk-dropdown-list">
                <li class="operate-item">
                    <bk-button
                        ext-cls="ai-script-button"
                        :disabled="readOnly"
                        @click="onWriteScript">
                        {{ $t('编写脚本') }}
                    </bk-button>
                </li>
                <li class="operate-item">
                    <bk-button
                        ext-cls="ai-script-button"
                        @click="onCheckScript">
                        {{ $t('脚本检查') }}
                    </bk-button>
                </li>
            </ul>
        </template>
    </bk-dropdown-menu>
</template>
<script>
    import bus from '@/utils/bus.js'
    export default {
        name: 'ScriptCodeDrownList',
        props: {
            readOnly: {
                type: Boolean,
                default: false
            },
            inputData: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
            }
        },
        methods: {
            // 编写脚本-打开对话框
            onWriteScript () {
                bus.$emit('writeScript')
            },
            // 脚本检查-生成标准化提示词,智能体检查
            onCheckScript () {
                bus.$emit('checkScript', this.inputData)
            }
        }
    }
</script>
<style lang="scss" scoped>
    ::v-deep .bk-dropdown-trigger{
        display: flex;
        align-items: center;
        justify-content: center;
    }
    ::v-deep .bk-dropdown-content{
        position: absolute;
        left: -25px !important;
        .operate-item {
            font-size: 12px !important;
            cursor: pointer;
            display: block;
            height: 32px;
            line-height: 33px;
            padding: 0 6px;
            text-decoration: none;
            white-space: nowrap;
            color: #63656e;
            &:hover {
                background-color: #eaf3ff;
                color: #3a84ff !important;
            }
            .ai-script-button{
                border: none;
                background: none;
                font-size: 12px;
                text-decoration: none;
                outline: none;
                height: 22px;
                line-height: 22px;
                padding: 0;
                &:hover {
                    color: #3a84ff;
                }
                &.bk-button.bk-default.is-disabled,
                &.bk-button.bk-default[disabled] {
                    color: #c4c6cc !important;
                }
            }
        }
    }
</style>
