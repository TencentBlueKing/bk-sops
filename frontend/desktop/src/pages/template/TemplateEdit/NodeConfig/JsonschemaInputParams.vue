<template>
    <div class="jsonschema-input-params">
        <bkui-form
            :value="inputFormData"
            form-type="horizontal"
            :schema="inputs"
            :layout="[]"
            @change="$emit('update', $event)">
        </bkui-form>
    </div>
</template>

<script>
    import createForm from '@blueking/bkui-form'
    import tools from '@/utils/tools.js'

    const BkuiForm = createForm()
    export default {
        name: 'JsonSchemaInputParams',
        components: {
            BkuiForm
        },
        props: {
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
                inputFormData: tools.deepClone(this.value)
            }
        },
        watch: {
            value (val) {
                this.inputFormData = tools.deepClone(val)
            }
        }
    }
</script>
<style scoped>

</style>
