<template>
  <div id="app">
      <b-navbar type="dark" sticky variant="dark" id="navbar">
      <b-navbar-nav>
        <b-navbar-brand active-class="active" class="nav-link" :to="{ name: 'Home'}"> <img class="logos d-inline-block align-top" id="logo" src="@/assets/app-logo.png"/> </b-navbar-brand>
        <b-nav-item class="nav-link" :to="{ name: 'Mapa centros'}">Mapa de Centros</b-nav-item>
        <b-nav-item class="nav-link" :to="{ name: 'Crear centro'}">Crear un Centro</b-nav-item>
        <b-nav-item class="nav-link" :to="{ name: 'Estadisticas'}">Estadísticas</b-nav-item>
      </b-navbar-nav>
      </b-navbar>
    <router-view ></router-view>
  </div>
</template>

<script>
  export default {
    name: 'App',
  }
</script>

<style>
  #app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    background-color: #fafafa;
  }
  #logo {
    align-self: center;
    height: 40px;
    width: 40px;
  }
  h2{
    padding-top: 50px;
  }

</style>
