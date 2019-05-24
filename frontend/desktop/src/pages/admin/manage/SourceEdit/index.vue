<template>
    <div class="source-edit">
        <edit-header></edit-header>
        <router-view></router-view>
    </div>
</template>
<script>
    import EditHeader from './EditHeader.vue'

    export default {
        name: 'SourceEdit',
        components: {
            EditHeader
        },
        data () {
            return {}
        },
        created () {}
    }
</script>
