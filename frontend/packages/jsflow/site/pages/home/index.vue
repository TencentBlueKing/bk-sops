<template>
    <div class="home-page">
        <div class="canvas-test">
            <js-flow :data="canvasData" @onBeforeDrop="onDragStop"></js-flow>
        </div>
        <div class="doc-container" v-html="doc"></div>
    </div>
</template>
<script>
    import marked from 'marked'
    import hljs from 'highlight.js'
    import 'highlight.js/styles/github.css';
    import mdString from '../../../README.md'
    import JsFlow from '../../../src/'

    const lines = [
        {
            id: 'line123feod03j26895c557a452252f0',
            source: {
                arrow: 'Right',
                id: 'nodeb662bc1afb5e60daa67e69f48de1'
            },
            target: {
                arrow: 'Left',
                id: 'node74b1ec6275b60d5c22c984842280'
            }
        },
        {
            id: 'line332309df3j26895c557a4522fd0d',
            source: {
                arrow: 'Top',
                id: 'node74b1ec6275b60d5c22c984842280'
            },
            target: {
                arrow: 'Left',
                id: 'node74b1ec6275b60d5c22c9848466f1'
            }
        },
        {
            id: 'line332309df3j26895c557a4522fdfs',
            source: {
                arrow: 'Bottom',
                id: 'node74b1ec6275b60d5c22c984842280'
            },
            target: {
                arrow: 'Left',
                id: 'node74b1ec6275b60d5c22c984842281'
            }
        },
        {
            id: 'line332309df3j26895c557a4522fdgf',
            source: {
                arrow: 'Right',
                id: 'node74b1ec6275b60d5c22c9848466f1'
            },
            target: {
                arrow: 'Left',
                id: 'noded782259a6895c557a452252ec65a'
            }
        },
        {
            id: 'line332309df3j26895c557a4522fdgf',
            source: {
                arrow: 'Right',
                id: 'node74b1ec6275b60d5c22c984842281'
            },
            target: {
                arrow: 'Top',
                id: 'noded782259a6895c557a452252ec65a'
            }
        }
    ]

    const nodes = [
        {
            id: 'nodeb662bc1afb5e60daa67e69f48de1',
            x: 120,
            y: 100,
            type: 'startpoint',
            anchor: ['Left', 'Right']
        },
        {
            id: 'node74b1ec6275b60d5c22c984842280',
            x: 280,
            y: 100,
            type: 'gateway',
            anchor: ['Top', 'Left', 'Bottom', 'Right']
        },
        {
            id: 'node74b1ec6275b60d5c22c984842281',
            x: 420,
            y: 60,
            type: 'tasknode',
            anchor: ['Top', 'Left', 'Bottom', 'Right']
        },
        {
            id: 'node74b1ec6275b60d5c22c9848466f1',
            x: 420,
            y: 140,
            type: 'tasknode',
            anchor: ['Top', 'Left', 'Bottom', 'Right']
        },
        {
            id: 'noded782259a6895c557a452252ec65a',
            x: 660,
            y: 100,
            type: 'endpoint',
            anchor: ['Left', 'Bottom']
        }
    ]

    export default {
        name: 'Home',
        components: {
            JsFlow
        },
        data () {
            return {
                doc: null,
                canvasData: {
                    nodes,
                    lines
                }
            }
        },
        created () {
            this.initDoc()
        },
        methods: {
            initDoc () {
                marked.setOptions({
                    highlight: function(code, lang) {
                        return hljs.highlightAuto(code).value;
                    }
                })
                this.doc = marked(mdString)
            },
            onDragStop (connector) {
                return true
            }
        }
    }
</script>
<style lang="scss">
    .home-page {
        margin: 0 auto;
        padding: 0 80px 20px;
        min-width: 1280px;
    }
    .canvas-test {
        margin: 40px 0 20px;
        height: 300px;
        z-index: 0;
    }
    .doc-container {
        pre {
            background-color: #f6f8fa;
            border-radius: 3px;
            font-size: 85%;
            line-height: 1.45;
            overflow: auto;
            padding: 16px;
        }
        blockquote {
            margin-left: 0;
            border-left: .25em solid #dfe2e5;
            color: #6a737d;
            padding: 0 1em;
        }
    }
</style>


