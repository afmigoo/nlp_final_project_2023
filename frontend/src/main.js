import { createApp } from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import router from './router';
import api from './api/index';

loadFonts()

const app = createApp(App);

app.use(router);

app.use(api);

app.use(vuetify);

app.config.globalProperties.$api = api;

app.mount('#app')

