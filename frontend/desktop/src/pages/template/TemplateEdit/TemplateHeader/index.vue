
<template>
    <div :class="['template-header-wrapper', { 'draft-header': type !== 'view' }]">
        <!--头部左侧-->
        <HeaderLeft
            :type="type"
            :name="name"
            :common="common"
            :template_id="template_id"
            :project_id="project_id"
            :tpl-actions="tplActions"
            :is-template-data-changed="isTemplateDataChanged"
            @goBackViewMode="$emit('goBackViewMode')">
        </HeaderLeft>
        <!--头部右侧-->
        <HeaderRightVue
            :type="type"
            :name="name"
            :common="common"
            :template_id="template_id"
            :project_id="project_id"
            :template-saving="templateSaving"
            :tpl-actions="tplActions"
            @onSaveTemplate="$emit('onSaveTemplate')"
            @onChangePanel="$emit('onChangePanel', $event)">
        </HeaderRightVue>
    </div>
</template>
<script>
    import HeaderLeft from './HeaderLeft.vue'
    import HeaderRightVue from './HeaderRight.vue'
    export default {
        name: 'TemplateHeader',
        components: {
            HeaderLeft,
            HeaderRightVue
        },
        props: {
            type: String,
            name: String,
            template_id: [String, Number],
            project_id: [String, Number],
            common: String,
            templateSaving: Boolean,
            isTemplateDataChanged: Boolean,
            tplActions: {
                type: Array,
                default () {
                    return []
                }
            }
        }
    }
</script>
<style lang="scss" scoped>
    .template-header-wrapper {
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 48px;
        font-size: 14px;
        padding: 0 20px 0 10px;
        background: #fff;
        box-shadow: 0 2px 4px 0 #0000001a;
        &.draft-header {
            height: 60px;
            /deep/.label {
                color: #63656e;
                background: #fafbfd;
                border: 1px solid #dcdee5;
            }
        }
    }
</style>
