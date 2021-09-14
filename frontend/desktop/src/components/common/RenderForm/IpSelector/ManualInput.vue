<template>
    <div class="manual-input">
        <p class="title">{{ $t('类型') }}</p>
        <bk-select
            v-model="selectorId"
            :clearable="false"
            :disabled="!editable"
            @change="onManualInputChange">
            <bk-option v-for="selector in selectorTabs.slice(0, -1)"
                :key="selector.id"
                :id="selector.id"
                :name="selector.name">
            </bk-option>
        </bk-select>
        <p class="title">{{ selectTypeTitle }}</p>
        <bk-input
            :placeholder="typeDes"
            :type="'textarea'"
            :disabled="!editable"
            v-model="inputValue"
            @change="onManualInputChange">
        </bk-input>
        <span v-show="dataError" class="common-error-tip error-info">{{ $t('必填项') }}</span>
    </div>
</template>

<script>
    export default {
        name: 'ManualInput',
        props: {
            selectorTabs: {
                type: Array,
                default: () => []
            },
            manualInput: {
                type: Object,
                default: () => {}
            },
            editable: {
                type: Boolean,
                default: false
            }
        },
        data () {
            const keys = Object.keys(this.manualInput)
            let selectorId, inputValue
            if (keys.length) {
                selectorId = this.manualInput.type
                inputValue = this.manualInput.value
            } else {
                selectorId = this.selectorTabs[0].id
                inputValue = ''
            }
            return {
                selectorId,
                inputValue,
                selectTypeTitle: '',
                dataError: false,
                typeDes: ''
            }
        },
        watch: {
            selectorId (val) {
                // 富文本标题
                const curSelector = this.selectorTabs.find(selector => selector.id === val)
                this.selectTypeTitle = curSelector && curSelector.name
                // 富文本description
                let desc = ''
                switch (val) {
                    case 'ip':
                        desc = this.$t('请输入IP，多个以逗号或者换行符隔开，在cmdb上唯一')
                        break
                    case 'topo':
                        desc = this.$t('请输入业务拓扑（形如：业务A>集群B>模块C），多个逗号或换行符隔开，在cmdb上唯一')
                        break
                    case 'group':
                        desc = this.$t('请输入动态分组名称，多个以逗号或换行符隔开，在cmdb上唯一')
                        break
                }
                this.typeDes = desc
            }
        },
        methods: {
            onManualInputChange () {
                const parmas = {
                    type: this.selectorId,
                    value: this.inputValue
                }
                this.$emit('change', parmas)
            },
            validate () {
                if (this.manualInput.value) {
                    this.dataError = false
                    return true
                } else {
                    this.dataError = true
                    return false
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    .manual-input {
        .bk-select {
            margin-bottom: 20px;
        }
        .title {
            margin-bottom: 6px;
        }
    }
</style>
