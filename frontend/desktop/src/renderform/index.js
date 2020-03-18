import RenderForm from './RenderForm.vue'

if (!window.gettext) {
    window.gettext = function (str) {
        return str
    }
}

const renderForm = {
    install: function(Vue){
        Vue.component('render-form', RenderForm)
    }
    
}

export default renderForm

export { renderForm }

if (typeof window !== 'undefined' && window.Vue) {
    window.Vue.use(renderForm)
 }