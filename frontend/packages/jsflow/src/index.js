import JsFlowVueComponents from './jsFlow/index.vue'

if (typeof window !== 'undefined' && 'Vue' in window) {
    window.Vue.component('js-flow', JsFlowVueComponents)
}

export default JsFlowVueComponents
