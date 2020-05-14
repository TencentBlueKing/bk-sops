import Vue from 'vue'
import VueI18n from 'vue-i18n'
import store from '../../store/index.js'
import en from './en.js'
import cn from './cn.js'

Vue.use(VueI18n)

const messages = {
    en,
    'zh-cn': cn
}
console.log(store, 'storestorestore')
// const localeLang = store.state.lang === 'en' ? 'zh-cn' : 'en'
// const localeLang = store.state.lang === 'en' ? 'en' : 'zh-cn'
const localeLang = getCookie('blueking_language') === 'en' ? 'en' : 'zh-cn'

const i18n = new VueI18n({
    locale: localeLang,
    messages
})

export default i18n
