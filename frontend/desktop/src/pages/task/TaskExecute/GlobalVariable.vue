<template>
    <div class="global-variable">
        <ul>
            <li
                class="variable-item"
                v-for="(variable, index) in globalVariablesList"
                :key="index">
                <p class="variable-label">{{ variable.key }}</p>
                <p class="variable-value">{{ variable.value }}</p>
            </li>
        </ul>
    </div>
</template>

<script>
    import { mapActions } from 'vuex'
    export default {
        props: {
            taskId: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                globalVariablesList: []
            }
        },
        mounted () {
            this.getGlobalVariablesList()
        },
        methods: {
            ...mapActions('task/', [
                'getRenderCurConstants'
            ]),
            // 获取所有全局变量当前渲染的值
            async getGlobalVariablesList () {
                try {
                    const resp = await this.getRenderCurConstants({ task_id: this.taskId })
                    this.globalVariablesList = resp.data
                } catch (error) {
                    console.warn(error)
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    .global-variable {
        padding: 24px;
        height: 100%;
        overflow-y: auto;
        @include scrollbar;
        .variable-item {
            margin-bottom: 16px;
            font-size: 12px;
            .variable-label {
                color: #63656e;
                margin-bottom: 8px;
            }
            .variable-value {
                min-height: 41px;
                width: 100%;
                background: #fafbfd;
                border: 1px solid #dcdee5;
                border-radius: 3px;
                padding: 12px 16px;
                line-height: 17px;
                color: #c4c6cc;
                word-break: break-all;
                cursor: not-allowed;
            }
        }
    }
</style>
