<template>
    <div class="jsonschema-input-params">
        <bkui-form
            ref="jsonschemaFormRef"
            form-type="horizontal"
            :value="inputFormData"
            :schema="inputs"
            :readonly="isViewMode"
            :context="context"
            :layout="{ group: [], container: { gap: '14px' } }"
            @change="$emit('update', $event)">
        </bkui-form>
    </div>
</template>

<script>
    import createForm from '@blueking/bkui-form'
    import '@blueking/bkui-form/dist/bkui-form.css'
    import tools from '@/utils/tools.js'

    const BkuiForm = createForm()
    export default {
        name: 'JsonSchemaInputParams',
        components: {
            BkuiForm
        },
        props: {
            isViewMode: Boolean,
            inputs: {
                type: Object,
                default: () => ({})
            },
            value: {
                type: Object,
                default: () => ({})
            }
        },
        data () {
            return {
                inputFormData: tools.deepClone(this.value),
                context: {
                    site_url: $.context.site_url,
                    project_id: $.context.project?.id
                }
            }
        },
        watch: {
            value (val) {
                this.inputFormData = tools.deepClone(val)
            }
        },
        methods: {
            validate () {
                return this.$refs.jsonschemaFormRef.validateForm()
            }
        }
    }
</script>
<style lang="scss" scoped>
    .jsonschema-input-params {
        >>> {
            .bk-schema-form-group-content {
                grid-auto-columns: 100%;
            }
            .bk-form-item {
                .bk-label {
                    width: 130px !important;
                    font-size: 12px;
                    & + .bk-form-content {
                        margin-left: 130px !important;
                    }
                }
                .bk-form-content {
                    font-size: 12px;
                    color: #63656e;
                }
                .bk-form-radio {
                    margin-right: 30px;
                    .bk-radio-text {
                        font-size: 12px;
                    }
                }
                .bk-form-checkbox {
                    margin-right: 30px;
                    .bk-checkbox-text {
                        font-size: 12px;
                    }
                }
            }
        }
    }
</style>
