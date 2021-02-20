<template>

  <div class="container">
    <div style="padding-top: 5px">
      <b-alert variant="success" :show="success.length > 0" dismissible @dismissed="resetErrors">
        <span>{{success}}</span>
      </b-alert>
    </div>
    <h2 class="display-4">{{titulo}}</h2>
    <p>
      {{descripcion}}
    </p>
    <div class="caja">
      <router-link to="/centros/" > <img class="logos" src="@/assets/mapa-logo.png"/> </router-link>
      <h3> Centros de Donaciones </h3>
      <div>
        <p>
          <router-link to="/centros/" >
          Ver en mapa </router-link>
        </p>
      </div>
    </div>
    <div class="caja">
      <router-link to="/centros/create"> <img class="logos" src="@/assets/centro.png"/>  </router-link>
      <h3>¿Quieres inscribir tu centro de Donaciones?</h3>
        <div>
          <p>
            Completa el <router-link to="/centros/create">formulario</router-link> para solicitar aprobacion de un nuevo centro de ayuda
          </p>
        </div>
    </div> 
    <div class="caja">
      <router-link :to="{ name: 'Estadisticas'}"> <img class="logos" src="@/assets/estadistica-logo.png"/> </router-link>
      <h3> Estadísticas </h3>
      <div>
        <p>
          <router-link :to="{ name: 'Estadisticas'}">Estadísticas</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'
  import { API_URL } from '@/store'
  export default {
    name: 'Home',
    data() {
        return{
            titulo: null,
            descripcion: null,
            success: ''
        }
    },
    beforeCreate: function () {
      axios.get(API_URL + '/api/configuration/datos_pagina')
        .then((res) => {
            this.titulo = res.data["datos"]["titulo"]
            this.descripcion = res.data["datos"]["descripcion"]
        })
    },
    mounted: function() {
        if (localStorage.getItem("success")) {
            this.success = localStorage.getItem("success")
            window.scrollTo(0,0)
        }
    },
    beforeDestroy: function() {
        if (localStorage.getItem("success")) {
            localStorage.removeItem("success")
        }
    },
    methods:{
        resetErrors(){
          localStorage.removeItem('success')
        }
    }
  }
</script>
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  
  .logos{
    max-width: 9%;
    height: auto;
    padding-top: 1%;
    display:inline;
    align-self: center;
    float: left;
  }
  
  .link{
    margin: auto;
    text-align:center;
  }

 .caja{
    border-radius: 8px;
    width: 80%;
    background: #e3f5f7;
    display: inline-block;
    flex-direction: column;
    position: relative;
    margin-left: auto;
    margin-right: auto;
    margin-top: 50px;
    padding: 0 10px; 
  }

  h3 {
    margin: 20px 0 0;
  }
  
  a {
    text-decoration: underline;
  }

</style>
