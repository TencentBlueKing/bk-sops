<template>
    <div class="shared-tpl-wrapper">
        <bk-button
            class="shared-btn"
            data-test-id="process_form_sharedProcess"
            :disabled="!selected.length"
            @click="openShowSlider">
            {{$t('共享到商店')}}
        </bk-button>
        <SharedTplSlider
            :is-show="isShowSlider"
            :selected="selected"
            :project_id="project_id"
            @close="closeShowSlider">
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
        },
        methods: {
<<<<<<< HEAD
            closeShowSlider () {
                this.isShowSlider = false
            },
            openShowSlider () {
                this.isShowSlider = true
            }
            
=======
            openShowSlider () {
                this.isShowSlider = true
            },
            closeShowSlider () {
                this.isShowSlider = false
            }
>>>>>>> release_humming_bird
        }
    }
</script>
<style lang="scss" scoped>

</style>
