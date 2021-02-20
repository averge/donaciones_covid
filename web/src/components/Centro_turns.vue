<template>
    <div class="container">
        <div style="padding-top: 5px">
            <b-alert variant="success" :show="success.length > 0" dismissible @dismissed="resetErrors">
                <span>{{success}}</span>
            </b-alert>
        </div>
        <h2 class="display-4"> Turnos de "{{center.nombre}}" </h2>
        <div class="row">
            <div class="col">
                <datepicker v-model="date" :language="es" @closed="nuevaFecha"></datepicker>
            </div>
        </div>
        <div v-if="errors.length > 0" >
            <h4 v-for="error in errors" v-bind:key="error['key']">{{ error }}<br></h4>
        </div>
        <div v-else-if="turns.length == 0">
            <h4> No hay turnos disponibles para esta fecha </h4>
        </div>
        <table v-else class="table">
            <thead>
                <tr>
                    <th scope="col">Hora Inicio </th>
                    <th scope="col">Hora Fin </th>
                    <th scope="col">Acciones</th> 
                </tr>
            </thead>
            <tbody>
                <tr v-for='turn in turns' v-bind:key='turn.hora_inicio'>
                    <td> {{turn.hora_inicio}} </td>
                    <td> {{turn.hora_fin}} </td>
                    <td> <router-link :to="{ name: 'Sacar turno', params: { turn: turn }}">Pedir</router-link> </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
import axios from 'axios'
import { API_URL } from '@/store'
import Datepicker from 'vuejs-datepicker';
import { es } from 'vuejs-datepicker/dist/locale'
export default {
    name: 'MostrarTurnos',
    components: {
        Datepicker
    },
    data() {
        return{
            es: es,
            date: null,
            turns: [],
            errors: [],
            center: null,
            success: '',
            centro_id: null,
        }
    },
    beforeCreate: function () {
        if (this.$route.params.center){
            this.centro_id = this.$route.params.center.id
            console.log(this.centro_id)
            if (localStorage.getItem("centro")) {
                localStorage.removeItem("centro")
            }
            localStorage.setItem("centro", this.$route.params.center.id)
        }else{
            this.centro_id = localStorage.getItem("centro") 
        }
        axios.get(API_URL + "/api/centros/" + this.centro_id + "/").then((res) => {
            this.center = res.data.atributos
        }).then(() => {
            var fecha = this.date.getDate() + "/"+ (this.date.getMonth()+1)+ "/" +this.date.getFullYear();
            axios.get(API_URL + '/api/centros/'+this.center.id+'/turnos_disponibles/?fecha='+fecha)
                .then((res) => {
                    this.turns = res.data["datos"]
                })
                .catch((error) => {
                    this.errors = error.response.data['messages'].split(',')
                })
        })
    },
    created: function() {
        if(this.$route.params.date){
            var f = this.$route.params.date.split("/")
            this.date = new Date((f[2]),(f[1]-1), f[0])
            if (localStorage.getItem("fecha")) {
                localStorage.removeItem("fecha")
            }
            localStorage.setItem("fecha", this.$route.params.date)
        }else{
            this.date = new Date()
            console.log("Asigne Fecha")
        }
    },
    mounted: function() {
        if (localStorage.getItem("success")) {
            this.success = localStorage.getItem("success")
        }
    },
    beforeDestroy: function() {
        if (localStorage.getItem("success")) {
            localStorage.removeItem("success")
        }
    },
    methods:{
        nuevaFecha: function(){
            var f = this.date
            var fecha = f.getDate() + "/"+ (f.getMonth()+1)+ "/" +f.getFullYear();
            axios.get(API_URL + '/api/centros/'+this.center.id+'/turnos_disponibles/?fecha='+fecha)
                .then((res) => {
                    this.turns = res.data["datos"]
                    this.errors = []
                })
                .catch((error) => {
                    this.errors = error.response.data['messages'].split(',')
                })
        },
        date1: function(){
            this.date = new Date(),
            this.nuevaFecha
        },
        resetErrors(){
          localStorage.removeItem('success')
        }
    }
}
</script>