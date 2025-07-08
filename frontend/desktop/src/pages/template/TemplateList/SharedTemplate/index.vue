<template>
    <div class="shared-tpl-wrapper">
        <bk-button
            class="shared-btn"
            data-test-id="process_form_sharedProcess"
            :disabled="!selected.length"
            @click="isShowSlider = true">
            {{$t('共享到商店')}}
        </bk-button>
        <SharedTplSlider
            :is-show="isShowSlider"
            :selected="selected"
            :project_id="project_id"
            @close="isShowSlider = false">
        </SharedTplSlider>
    </div>
</template>
<script>
    import SharedTplSlider from './SharedTplSlider.vue'
    export default {
        name: 'sharedTemplate',
        components: {
            SharedTplSlider
        },
        props: {
            project_id: [String, Number],
            selected: {
                type: Array,
                default: () => ([])
            }
        },
        data () {
            return {
                isShowSlider: false
            }
        }
    }
</script>
<style lang="scss" scoped>

</style>
