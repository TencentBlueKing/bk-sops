<template>
    <template-list common="1" :cc_id="cc_id"></template-list>
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
            ...mapState({
                cc_id: state => state.cc_id
            })
        }
    }
</script>
