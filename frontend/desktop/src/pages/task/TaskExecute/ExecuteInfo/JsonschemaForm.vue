<template>
    <div class="jsonschema-input-params">
        <bkui-form
            form-type="horizontal"
            readonly
            :value="formData"
            :schema="schema"
            :layout="{ group: [], container: { gap: '10px' } }">
        </bkui-form>
    </div>
</template>

<script>
    import createForm from '@blueking/bkui-form'
    import '@blueking/bkui-form/dist/bkui-form.css'
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
