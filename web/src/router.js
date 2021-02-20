import Vue from 'vue'
import Router from 'vue-router'
import Home from './components/Home.vue'


Vue.use(Router)

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home,
    },
    {
        path: '/centros/',
        name: 'Mapa centros',
        component: function () { return import('./components/Centro_map.vue')},
    },
    {
        path: '/centros/create/',
        name: 'Crear centro',
        component: function () { return import('./components/Centro_create.vue')},
    },
    {
        path: '/centros/turnos/',
        name: 'Mostrar turnos',
        component: function () { return import('./components/Centro_turns.vue')},
    },
    {
        path: '/centros/turnos/create/',
        name: 'Sacar turno',
        component: function () { return import('./components/Turno_create.vue')},
    },
    {
        path: '/centro/',
        name: 'Mostrar centro',
        component: function () { return import('./components/Centro_show')},
    },
    {
        path: '/estadisticas/',
        name: 'Estadisticas',
        component: function() { return import ('./components/Estadisticas')},
    }
]

const router = new Router({
    mode: 'history',
    base: process.env.BASE_URL,
    routes,
})

export default router