<template>
    <div class="jsonschema-input-params">
        <bkui-form
            :value="inputFormData"
            form-type="horizontal"
            :schema="inputs"
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
<style lang="scss" scoped>
  .jsonschema-input-params {
      >>> .bk-form-item {
          .bk-label {
             width: 130px !important;
             font-size: 12px;
          }
          .bk-form-content {
              margin-left: 130px !important;
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
</style>
