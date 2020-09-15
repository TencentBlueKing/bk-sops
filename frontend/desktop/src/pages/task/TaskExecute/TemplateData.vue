<template>
    <div class="pipeline-tree-wrap">
        <div class="code-wrapper">
            <code-editor
                v-if="templateData"
                :value="templateData"
                :options="{ readOnly: true, language: 'json' }">
            </code-editor>
            <no-data v-else></no-data>
        </div>
        <div class="action-wrapper">
            <bk-button theme="primary" @click="onshutDown">{{ $t('关闭') }}</bk-button>
        </div>
    </div>
</template>
<script>
    import CodeEditor from '@/components/common/CodeEditor.vue'
    import NoData from '@/components/common/base/NoData.vue'
    export default {
        name: 'TemplateData',
        components: {
            CodeEditor,
            NoData
        },
        props: {
            templateData: {
                type: String,
                default: ''
            }
        },
        methods: {
            onshutDown () {
                this.$emit('onshutDown')
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '@/scss/config.scss';
    @import '@/scss/mixins/scrollbar.scss';
    .pipeline-tree-wrap {
        height: 100%;
    }
    .code-wrapper {
        position: relative;
        padding: 20px;
        height: calc(100% - 60px);
    }
    .action-wrapper {
        padding-left: 20px;
        height: 60px;
        line-height: 60px;
        border-top: 1px solid $commonBorderColor;
    }
</style>
