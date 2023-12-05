<template>
    <div class="plugin-field-config">
        <div class="header">
            <i class="common-icon-arrow-left" @click="$emit('closePanel')"></i>
            <span>{{ $t('插件字段配置') }}</span>
        </div>
        <VariableCitedConfigVue
            :is-select="true"
            :variable-data="variableData"
            :variable-cited="variableCited"
            :hook-params="hookParams"
            @onAddVariable="$emit('onAddVariable', $event)"
            @onEditVariable="$emit('onEditVariable', $event)"
            @update="selectedVarKey = $event">
        </VariableCitedConfigVue>
        <div class="btn-wrap">
            <bk-button theme="primary" @click="onUseVariable">{{ $t('使用变量') }}</bk-button>
            <bk-button @click="$emit('closePanel')">{{ $t('取消') }}</bk-button>
        </div>
    </div>
</template>

<script>
    import bus from '@/utils/bus.js'
    import VariableCitedConfigVue from './VariableCitedConfig.vue'
    export default {
        name: 'PluginFieldConfig',
        components: {
            VariableCitedConfigVue
        },
        props: {
            variableCited: Object,
            variableData: Object,
            hookParams: Object
        },
        data () {
            return {
                selectedVarKey: this.variableData.key
            }
        },
        methods: {
            onUseVariable () {
                const { cited_info: citedInfo = {} } = this.variableData
                bus.$emit('useVariable', {
                    type: 'replace',
                    code: citedInfo.tagCode,
                    key: this.selectedVarKey,
                    variable: {
                        key: this.selectedVarKey,
                        type: 'reuse',
                        cited_info: citedInfo
                    }
                })
                this.$emit('closePanel')
            }
        }
    }
</script>

<style lang="scss" scoped>
@import '@/scss/mixins/scrollbar.scss';
.plugin-field-config {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: #fff;
    .header {
        display: flex;
        align-items: center;
        padding: 16px;
        line-height: 22px;
        font-size: 14px;
        color: #63656e;
        border-bottom: 1px solid #dcdee5;
        i {
            font-size: 12px;
            color: #3a84ff;
            margin-right: 8px;
            cursor: pointer;
        }
    }
    .variable-cited-wrap {
        flex: 1;
        overflow-y: auto;
        @include scrollbar;
    }
    .btn-wrap {
        padding: 8px 30px;
        background: #fafbfd;
        border-top: 1px solid #cacedb;
        .bk-button {
            margin-right: 10px;
            padding: 0 25px;
        }
    }
}
</style>
