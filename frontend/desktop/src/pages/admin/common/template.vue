<template>
    <template-list :common="1" :project_id="project_id"></template-list>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState } from 'vuex'
    import TemplateList from '@/pages/template/TemplateList/index.vue'

    export default {
        name: 'CommonTemplate',
        components: {
            TemplateList
        },
        computed: {
            ...mapState('project', {
                project_id: state => state.project_id
            })
        }
    }
</script>
