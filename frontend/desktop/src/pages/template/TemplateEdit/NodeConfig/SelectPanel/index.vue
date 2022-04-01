<template>
    <div class="select-panel">
        <subflow
            v-if="isSubflow"
            :common="common"
            :basic-info="basicInfo"
            :template-labels="templateLabels"
            @select="$emit('select', $event)">
        </subflow>
        <plugin
            v-else
            :basic-info="basicInfo"
            :built-in-plugin="atomTypeList.tasknode"
            :third-party-plugin="atomTypeList.pluginList"
            @select="$emit('select', $event)">
        </plugin>
    </div>
</template>
<script>
    import Plugin from './plugin.vue'
    import Subflow from './subflow.vue'

    export default {
        name: 'SelectPanel',
        components: {
            Plugin,
            Subflow
        },
        props: {
            project_id: [String, Number],
            templateLabels: Array, // 模板标签
            atomTypeList: Object,
            isSubflow: Boolean,
            basicInfo: Object,
            isThirdParty: Boolean,
            common: [String, Number],
            pluginLoading: Boolean
        },
        data () {
            return {}
        }
    }
</script>
<style lang="scss" scoped>
.select-panel {
    position: relative;
}
</style>
