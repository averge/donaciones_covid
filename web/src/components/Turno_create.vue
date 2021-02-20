<template>
    <div class="container">
        <h2 class="display-4"> Crear Turno de "Centro" </h2>
        <form v-on:submit.prevent="submitForm">
            <b-alert variant="danger" :show="errors.length > 0" dismissible @dismissed="resetErrors">
                <span v-for="error in errors" v-bind:key="error['key']">{{ error }}<br></span>
            </b-alert>
            <div class="form-group row">
                <label for="fecha"> Fecha </label>
                <input type="text" class="form-control" id="fecha" v-model="form.fecha" readonly>
            </div>
            <div class="form-group row">
                <label for="hora_inicio"> Hora Inicio </label>
                <input type="text" class="form-control" id="hora_inicio" v-model="form.hora_inicio" readonly>
            </div>
            <div class="form-group row">
                <label for="hora_fin"> Hora Fin </label>
                <input type="text" class="form-control" id="hora_fin" v-model="form.hora_fin" readonly>
            </div>
            <div class="form-group row">
                <label for="email"> Mail de contacto </label>
                <input type="email" class="form-control" id="email" v-model="form.email_donante" placeholder="ejemplo@mail.com" required>
            </div>
            <div class="form-group row">
                <label for="phone_number"> Telefono de contacto </label>
                <input type="text" class="form-control" id="phone_number" v-model="form.telefono_donante" placeholder=" xxx - xxxxxxx" required>
            </div>
            <div class="form-group">
                <button class="btn btn-primary mr-2">Crear</button>
                <router-link tag="button" class="btn btn-secondary" to="/">Cancelar</router-link>
            </div>
        </form>
    </div>
</template>

<script>
import axios from 'axios'
import { API_URL } from '@/store'
export default {
    name: 'CrearTurno',
    data (){
        return{
            errors: [],
            center: null,
            showDismissibleAlert: true,
            dismissSecs: 10,
            dismissCountDown: 0,
            form: {
                hora_inicio: null,
                hora_fin: null,
                fecha: null,
                email_donante: null,
                telefono_donante: null,
            },
        }
    },
    created: function(){
        if (this.$route.params.turn){
            this.center = this.$route.params.turn.centro_id
            if (localStorage.getItem("centro")) {
                localStorage.removeItem("centro")
            }
            localStorage.setItem("centro", this.$route.params.turn.centro_id)
            
            this.form.hora_inicio = this.$route.params.turn.hora_inicio
            if (localStorage.getItem("hora_inicio")) {
                localStorage.removeItem("hora_inicio")
            }
            localStorage.setItem("hora_inicio", this.$route.params.turn.hora_inicio)

            this.form.hora_fin = this.$route.params.turn.hora_fin
            if (localStorage.getItem("hora_fin")) {
                localStorage.removeItem("hora_fin")
            }
            localStorage.setItem("hora_fin", this.$route.params.turn.hora_fin)

            this.form.fecha = this.$route.params.turn.fecha
            if (localStorage.getItem("fecha")) {
                localStorage.removeItem("fecha")
            }
            localStorage.setItem("fecha", this.$route.params.turn.fecha)

        }else{
            this.center = localStorage.getItem("centro")
            this.form.hora_inicio = localStorage.getItem("hora_inicio")
            this.form.hora_fin = localStorage.getItem("hora_fin")
            this.form.fecha = localStorage.getItem("fecha")
        }
    },
    methods:{
      submitForm(){
        axios.post(API_URL + '/api/centros/'+this.center+'/reserva', this.form)
          .then(() => {
            localStorage.setItem("success", "El turno fue creado correctamente")
            this.$router.push({name: 'Mostrar turnos', params: { centerId: this.center, date: this.form.fecha}});
          })
          .catch((error) => {
            this.errors = error.response.data['messages'].split(',')
          })
      },
      resetErrors(){
          this.errors = []
      }
    }
}
</script>