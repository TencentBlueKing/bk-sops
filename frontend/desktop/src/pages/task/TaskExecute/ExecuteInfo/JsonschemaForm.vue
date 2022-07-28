<template>
    <div class="jsonschema-input-params">
        <bkui-form
            :value="formData"
            form-type="horizontal"
            :schema="schema"
            :layout="[]">
        </bkui-form>
    </div>
</template>

<script>
    import createForm from '@blueking/bkui-form'
    import tools from '@/utils/tools.js'

    const BkuiForm = createForm()
    export default {
        name: 'JsonSchemaForm',
        components: {
            BkuiForm
        },
        props: {
            schema: {
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
                formData: tools.deepClone(this.value)
            }
        },
        watch: {
            value (val) {
                this.formData = tools.deepClone(val)
            }
        }
    }
</script>
