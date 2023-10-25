import { createRouter, createWebHashHistory } from 'vue-router';
import MainWindow from './components/MainWindow.vue';
import SearchResults from './components/SearchResults.vue';

const routes = [
    { path: '/main', component: MainWindow, alias: '/' },
    { path: '/result', component: SearchResults},
]

const router = createRouter({
    history: createWebHashHistory(),
    routes,
})

export default router