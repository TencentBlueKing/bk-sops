<template>
    <content-loader
        :width="1366"
        :height="600"
        :style="{ 'transform': `scaleX(${contentWidth / baseWidth})` }"
        :speed="loadingConf.speed"
        :primary-color="loadingConf.primaryColor"
        :secondary-color="loadingConf.secondaryColor">
        <path d="M 927 50 h 80 v 20 h -80 z" />
        <path d="M 1046 44 h 320 v 32 h -320 z" />
        <path d="M 0 123 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 171 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 219 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 267 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 365 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 415 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 463 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
        <path d="M 0 317 h 1366 v 24 H 0 v -24 z m 0 0 h 1366 v 24 H 0 v -24 z" />
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
            baseWidth: {
                type: Number,
                default: 1366
            },
            contentWidth: {
                type: Number,
                default: 1366
            },
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
