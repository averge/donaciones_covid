<template>
  <div class="container">
    <h2 class="display-4">{{centro.nombre}} </h2>
    <div class="row">
        <div class="col-left">
            <div style="text-align: left;">
                Direccion: {{centro.direccion}} <br>
                Telefono: {{centro.telefono}}  <br>
                Horario de apertura: {{centro.hora_apertura}} <br>
                Horario de cierre: {{centro.hora_cierre}} <br>
                Tipo: {{tipo_formateado}} <br>
                Municipio: {{municipio_nombre}} <br>
                Direccion Web: {{centro.web}} <br>
                Email: {{centro.email}} <br>
                <router-link :to="{ path:'/centros/turnos/', name: 'Mostrar turnos', params: { center: centro }}">Sacar Turno</router-link>
            </div>
        </div>
        <div class="col">
            <l-map
                style="height: 360px; width: 100%"
                :zoom="zoom"
                :center="centro.coordenadas"
            >
            <l-marker :lat-lng="centro.coordenadas" ></l-marker>
            <l-tile-layer :url="url"></l-tile-layer>
        </l-map>
        </div>
    </div>
  </div>
</template>

<script>
    import axios from 'axios' 

    import { LMap, LTileLayer, LMarker } from 'vue2-leaflet'
    
    import 'leaflet/dist/leaflet.css'
    
    import { Icon } from 'leaflet';
    delete Icon.Default.prototype._getIconUrl;
    Icon.Default.mergeOptions({
        iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
        iconUrl: require('leaflet/dist/images/marker-icon.png'),
        shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
    });

    import { MUNICIPIOS_URL, API_URL } from '@/store'


    export default {
        name: 'MostrarCentro',
        components: {
                LMap,
                LTileLayer,
                LMarker,
        },
        data() {
            return {
                centro_id: null,
                centro: null,
                url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                zoom: 14,
                municipio_nombre: '',
                tipo_formateado: null,
            }
        },
        beforeCreate:function ()  {
            if (this.$route.params.center){
                this.centro_id = this.$route.params.center.id
                if (localStorage.getItem("centro")) {
                    localStorage.removeItem("centro")
                }
                localStorage.setItem("centro", this.$route.params.center.id)
            }else{
               this.centro_id = localStorage.getItem("centro") 
            }
            axios.get(API_URL + "/api/centros/" + this.centro_id + "/").then((res) => {
                this.centro = res.data.atributos
            }).then(() => {
                axios.get(MUNICIPIOS_URL)
                .then((res) => {
                    var towns = res.data["data"]["Town"]
                    for(let key in Object.keys(towns)) {
                    if(towns[key] && towns[key]["id"] == this.centro.municipio.id) {
                        this.municipio_nombre = towns[key]['name']
                    }
                    }
                    this.tipo_formateado = this.centro.tipo.replaceAll('_', ' ')
                })
            })
        },
    }
</script>

