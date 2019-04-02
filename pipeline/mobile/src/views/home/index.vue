<template>
    <div class="home-page">
    </div>
</template>
<script>
    import { mapActions } from 'vuex'

    export default {
        name: 'Home',
        data () {
            return {
                templateList: []
            }
        },
        mounted () {
            this.loadData()
        },
        methods: {
            ...mapActions('templateList', [
                'getTemplateList'
            ]),
            async loadData () {
                this.templateList = await this.getTemplateList()
            }
        }
    }
</script>
