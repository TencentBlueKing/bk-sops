<template lang="html">
    <div :class="[{ 'ag-loading-content': isLoaderShow, 'loading': localLoading, 'fadeout': !localLoading }]" :style="{ 'min-height': localLoading && height ? height + 'px' : '100%' }">
        <div :class="['loading-loader', { 'hide': !isLoaderShow }]" :style="{ 'background-color': backgroundColor }">
            <template v-if="loader">
                <component :is="loader"></component>
            </template>
            <template v-else>
                <div class="bk-loading" style="position: absolute; z-index: 10; background-color: rgba(255, 255, 255, 0.9);">
                    <div class="bk-loading-wrapper">
                        <div class="bk-loading1 bk-colorful bk-size-large">
                            <div class="point point1"></div>
                            <div class="point point2"></div>
                            <div class="point point3"></div>
                            <div class="point point4"></div>
                        </div>
                    </div>
                </div>
            </template>
        </div>
        <slot></slot>
    </div>
</template>

<script>
    function registerLoaders () {
        const loaderComponents = {}
        const loaderFiles = require.context(
            './loaders/',
            false,
            /\w+\.vue$/
        )
        loaderFiles.keys().forEach(key => {
            const componentConfig = loaderFiles(key)
            const comp = componentConfig.default
            loaderComponents[comp.name] = comp
        })

        return loaderComponents
    }

    export default {
        components: {},
        props: {
            loading: {
                type: Boolean,
                default: true
            },
            loader: {
                type: String
            },
            width: {
                type: Number
            },
            height: {
                type: Number
            },
            delay: {
                type: Number,
                default: 300
            },
            backgroundColor: {
                type: String,
                default: '#f4f7fa'
            }
        },
        data () {
            return {
                localLoading: this.loading,
                isLoaderShow: this.loading
            }
        },
        watch: {
            loading (newVal, oldVal) {
                // true转false时，让loading动画再运行一段时间，防止过快而闪烁
                if (oldVal && !newVal) {
                    setTimeout(() => {
                        this.localLoading = this.loading
                        setTimeout(() => {
                            this.isLoaderShow = this.loading
                        }, 200)
                    }, this.delay)
                } else {
                    this.localLoading = this.loading
                    this.isLoaderShow = this.loading
                }
            }
        },
        beforeCreate () {
            const loaderComponents = registerLoaders()
            Object.keys(loaderComponents).forEach(name => {
                this.$options.components[name] = loaderComponents[name]
            })
        }
    }
</script>

<style lang="scss" scoped>
    .ag-loading-content {
        position: relative;
        overflow: hidden;

        &.loading {
            * {
                opacity: 0 !important;
            }
        }

        &.fadeout {
            .loading-loader {
                opacity: 0 !important;
            }
        }

        .loading-loader {
            display: flex;
            justify-content: flex-start;
            align-items: flex-start;
            position: absolute;
            width: 100%;
            height: 100%;
            left: 0;
            right: 0;
            top: 0;
            bottom: 0;
            z-index: 100;
            transition: opacity ease 0.5s;
            opacity: 1 !important;

            &.hide {
                z-index: -1;
            }

            svg {
                width: 100%;
            }

            * {
                opacity: 1 !important;
            }
        }
    }
    .hide {
        display: none;
    }
</style>
