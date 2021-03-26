<template>
    <content-loader
        :width="1366"
        :height="600"
        :speed="loadingConf.speed"
        :primary-color="loadingConf.primaryColor"
        :secondary-color="loadingConf.secondaryColor">
        <path d="M 940 6 h 80 v 20 h -80 z" />
        <path d="M 1046 0 h 360 v 32 h -360 z" />
        <path d="M 0 52 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 92 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 132 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 172 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 212 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 252 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 292 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 332 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 372 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 412 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
    </content-loader>
</template>

<script>
    import { ContentLoader } from 'vue-content-loader'
    export default {
        name: 'commonList',
        components: {
            ContentLoader
        },
        props: {
            loadingConf: {
                type: Object,
                default () {
                    return {
                        primaryColor: '#ebecf3',
                        secondaryColor: '#f6f7fb'
                    }
                }
            }
        }
    }
</script>
