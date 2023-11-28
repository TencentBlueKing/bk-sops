
<template>
    <div :class="['template-header-wrapper', { 'draft-header': type !== 'view' }]">
        <!--执行方案头-->
        <div class="exec-schema-wrap" v-if="isExecSchemaView">
            <div v-if="isExecSchemaView" class="header-left-area">
                <i class="bk-icon icon-arrows-left back-icon" @click="$emit('onChangePanel', '')"></i>
                <span v-bk-overflow-tips class="template-name">{{ name }}</span>
            </div>
            <div
                v-if="isExecSchemaPreview"
                class="button-area preview"
                data-test-id="templateEdit_form_closePreview">
                <bk-button theme="primary" @click="$emit('onClosePreview')">{{ $t('关闭预览') }}</bk-button>
            </div>
        </div>
        <!--模板头-->
        <template v-else>
            <!--头部左侧-->
            <HeaderLeft
                :type="type"
                :name="name"
                :common="common"
                :template_id="template_id"
                :project_id="project_id"
                :tpl-actions="tplActions"
                :collect-info="collectInfo"
                :is-template-data-changed="isTemplateDataChanged"
                @goBackViewMode="$emit('goBackViewMode')"
                @onChangePanel="$emit('onChangePanel', $event)">
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
                :draft-update-info="draftUpdateInfo"
                :published="published"
                @templateDataChanged="$emit('templateDataChanged', $event)"
                @onPublishDraft="$emit('onPublishDraft')"
                @onChangePanel="$emit('onChangePanel', $event)">
            </HeaderRightVue>
        </template>
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
            },
            collectInfo: {
                type: Object,
                default: () => ({})
            },
            published: Boolean,
            draftUpdateInfo: {
                type: Object,
                default: () => ({})
            },
            isExecSchemaView: Boolean,
            isExecSchemaPreview: Boolean
        }
    }
</script>
<style lang="scss" scoped>
    .template-header-wrapper {
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 48px;
        position: relative;
        font-size: 14px;
        padding: 0 20px 0 10px;
        background: #fff;
        z-index: 12;
        box-shadow: 0 2px 4px 0 #0000001a;
        .exec-schema-wrap {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            .header-left-area {
                display: flex;
                align-items: center;
                .back-icon {
                    font-size: 28px;
                    color: #3a84ff;
                    cursor: pointer;
                }
                .template-name {
                    color: #63656e;
                    margin-right: 9px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
            }
        }
        &:hover {
            /deep/.icon-edit-line {
                display: inline-block !important;
            }
        }
        &.draft-header {
            height: 60px;
            /deep/.label {
                color: #63656e;
                background: #fafbfd;
                border: 1px solid #dcdee5;
            }
        }
        &:has(~.side-edit-active) {
            z-index: 113;
            &::before {
                content: '';
                display: block;
                position: absolute;
                height: 100%;
                width: 100%;
                z-index: 2;
            }
        }
    }
</style>
