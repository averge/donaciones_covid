<template>
  <div class="container">
    <h2 class="display-4"> Cargar centro de ayuda </h2>
    <form v-on:submit.prevent="submitForm">
      <b-alert variant="danger" :show="errors.length > 0" dismissible @dismissed="resetErrors">
        <span v-for="error in errors" v-bind:key="error['key']">{{ error }}<br></span>
      </b-alert>
      <div class="form-group row">
        <label for="nombre">Nombre del centro de ayuda</label>
        <input type="text" class="form-control" id="nombre" placeholder="Merendero Todos por una Sonrisa" v-model="form.nombre" required>
      </div>
      <div class="form-group row">
        <label for="direccion">Direccion</label>
        <input type="text" class="form-control" id="nombre" placeholder="Calle 88 nro 1912, Altos de San Lorenzo" v-model="form.direccion" required>
      </div>
      <div class="form-group row">
        <label for="telefono">Telefono (Incluir numero de area)</label><br>
        <input type="tel" class="form-control" id="telefono" placeholder="221 - 5930941" v-model="form.telefono" required>
      </div>
      <div class="form-group row">
        <div class="col">
          <label for="opens_at_hour">Horario de apertura</label><br>
          <b-form-timepicker minutes-step="30" id="opens_at_hour" v-model="form.hora_apertura"></b-form-timepicker>
        </div>
        <div class="col">
          <label for="closes_at_hour">Horario de cierre</label><br>
          <b-form-timepicker minutes-step="30" id="closes_at_hour" v-model="form.hora_cierre"></b-form-timepicker>
          </div>
      </div>
      <div class="form-group">
        <label for="tipo_centro">Tipo de centro</label><br>
        <select id="tipo_centro" class="custom-select" v-model="form.tipo" required>
          <option v-for="tipo in tipos" v-bind:key="tipo.id" :value="tipo.id">
            {{tipo.value}}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label for="municipio">Municipio</label><br>
        <select id="municipio" class="custom-select" v-model="form.municipio" required>
          <option v-for="muni in municipios" v-bind:key="muni.id" :value="muni.id">
            {{muni.name}}
          </option>
        </select>
      </div>
      <div class="form-group row">
        <label for="web">Dirección web</label><br>
        <input type="text" class="form-control" id="web" placeholder="https://www.google.com" v-model="form.web">
      </div>
      <div class="form-group row">
        <label for="email">Dirección de email</label><br>
        <input type="email" class="form-control" id="email" placeholder="ejemplo@centro-ayuda.org.ar" v-model="form.email">
      </div>
      <div>
        <l-map
          style="height: 360px; width: 100%"
          :zoom="zoom"
          :center="center"
          @click="addMarker"
        >
          <l-tile-layer :url="url"></l-tile-layer>
        <l-marker v-for="marker in markers" v-bind:key="marker.lat" :lat-lng="marker" @click="removeMarker()"></l-marker>        </l-map>
      </div>
      <div class="form-group row" style="padding-top: 20px">
        <vue-recaptcha
          :sitekey="sitekey"
          :loadRecaptchaScript="true"
          @verify="onVerify"
        ></vue-recaptcha>
      </div>
      <div class="form-group" style="padding-top: 20px">
        <button class="btn btn-primary mr-2">Crear</button>
        <router-link tag="button" class="btn btn-secondary" to="/">Cancelar</router-link>
      </div>
    </form>
  </div>
</template>

<script>
  import VueRecaptcha from 'vue-recaptcha';
  import axios from 'axios'
  
  import { LMap, LTileLayer, LMarker } from 'vue2-leaflet'


  import 'leaflet/dist/leaflet.css'
    
  import { Icon } from 'leaflet';

  import { MUNICIPIOS_URL, API_URL } from '@/store'
  delete Icon.Default.prototype._getIconUrl;
  Icon.Default.mergeOptions({
      iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
      iconUrl: require('leaflet/dist/images/marker-icon.png'),
      shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
  });

  export default {
    name: 'CrearCentro',
    components: {
      LMap,
      LTileLayer,
      LMarker,
      VueRecaptcha
    },
    data(){
      return{
        errors: [],
        municipios: [],
        tipos: [],
        form: {
          nombre: null,
          direccion: null,
          telefono: null,
          hora_apertura: null,
          hora_cierre: null,
          tipo: null,
          municipio: null,
          web: "",
          email: "",
          coordenadas: null,
        },
        showDismissibleAlert: true,
        dismissSecs: 10,
        dismissCountDown: 0,
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        zoom: 14,
        center: [-34.92145, -57.95453],
        markers: [],
        sitekey: "6LeKf_0ZAAAAAGmyYN_h5wQjdmoOIEh3O5OYA0hO",
        captchaVerified: false,
      }
    },
    beforeCreate: function () {
      axios.get(MUNICIPIOS_URL)
        .then((res) => {
          var towns = res.data["data"]["Town"]
          for(let key in Object.keys(towns)) {
            if(towns[key]) {
              this.municipios.push(towns[key])
            }
          }
        })
      axios.get(API_URL + '/api/tipos/')
        .then((res) => {
          for(var i = 0; i < res.data["datos"].length; i++) {
            var dict = {}
            dict["id"] = res.data['datos'][i]
            dict["value"] = res.data['datos'][i].replaceAll('_', ' ')
            this.tipos.push(dict) 
          }
        })
    },
    methods:{
      submitForm(){
        var abre = document.querySelector("#opens_at_hour__value_")
        var cierre = document.querySelector("#closes_at_hour__value_")
        var fallo = false
        if (abre.innerHTML == "No time selected") {
          fallo = true
          this.errors.push("La fecha de apertura no puede estar vacia")
        }
        if (cierre.innerHTML == "No time selected") {
          fallo = true
          this.errors.push("La fecha de cierre no puede estar vacia")
        }
        if (! this.form.coordenadas){
          fallo = true
          this.errors.push("Elija una ubicacion en el mapa")
        }
        if (! this.captchaVerified){
          fallo = true
          this.errors.push("Verifique el captcha")
        }
        if (!fallo) {
          this.form.municipio = {"id": parseInt(this.form.municipio, 10)}
          axios.post(API_URL + '/api/centros/', this.form)
            .then(() => {
              localStorage.setItem("success", "La solicitud de creacion de centro de ayuda fue mandada correctamente")
              this.$router.push({name: 'Home'});
            })
            .catch((error) => {
              this.errors = error.response.data['messages'].split(',')
            })
        }
      },
      removeMarker() {
        this.markers = []
        this.form.coordenadas = null
      },
      addMarker(event) {
        if (this.markers.length > 0) {
          this.markers = []
        }
        this.markers.push(event.latlng)
        this.form.coordenadas = [this.markers[0].lat,this.markers[0].lng]
      },
      resetErrors(){
        this.errors = []
      },
      onVerify(){
        this.captchaVerified = true
      }
    }
  }
</script>