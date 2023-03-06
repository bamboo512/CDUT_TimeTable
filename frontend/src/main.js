import { createApp } from 'vue'
import App from './App.vue'
import { VueClipboard } from '@soerenmartius/vue3-clipboard'
import router from './router'
import './assets/tailwind.css'
import VueToast from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';
import store from './store'




createApp(App)
    .use(router)
    .use(VueClipboard)
    .use(store)
    .use(VueToast)
    .mount('#app')
