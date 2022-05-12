<template>
    <div class="select-panel">
        <subflow
            v-if="nodeConfig.type === 'SubProcess'"
            :common="common"
            :node-config="nodeConfig"
            :template-labels="templateLabels"
            @select="$emit('select', $event)">
        </subflow>
        <plugin
            v-else
            :crt-plugin="basicInfo.plugin"
            :built-in-plugin="atomTypeList.tasknode"
            :is-third-party="isThirdParty"
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
            isThirdParty: Boolean,
            nodeConfig: {
                type: Object,
                default: () => ({})
            },
            basicInfo: Object,
            common: [String, Number]
        }
    }
</script>
<style lang="scss" scoped>
.select-panel {
    position: relative;
}
</style>
