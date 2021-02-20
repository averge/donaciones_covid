<template>
    <div class="container">
        <h2 class="display-4">Mapa de centros</h2>
        <l-map
            style="height: 420px; width: 100%"
            :zoom="zoom"
            :center="center"
        >
        <l-marker v-for="centro in centros" v-bind:key="centro.id" :lat-lng="centro['coordenadas']" >
            <l-popup>
                {{centro.nombre}}<br>
                Direccion: {{centro.direccion}}<br>
                Telefono: {{centro.telefono}}<br>
                Abre a: {{centro.hora_apertura}}<br>
                Cierra a: {{centro.hora_cierre}}<br>
                <router-link :to="{ name: 'Mostrar centro', params: { center:centro }}">Detalles</router-link>
            </l-popup>
        </l-marker>
            <l-tile-layer :url="url"></l-tile-layer>
        </l-map>
        

    </div>
</template>

<script>
    import axios from 'axios'
    import { LMap, LTileLayer, LMarker, LPopup } from 'vue2-leaflet';
    import 'leaflet/dist/leaflet.css';
    
    import { Icon } from 'leaflet';
    import { API_URL } from '@/store'

    delete Icon.Default.prototype._getIconUrl;
    Icon.Default.mergeOptions({
        iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
        iconUrl: require('leaflet/dist/images/marker-icon.png'),
        shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
    });

    export default {
        name: 'MapaCentros',
        components: {
            LMap,
            LTileLayer,
            LMarker,
            LPopup,
        } ,
        data() {
            return {
                centros: [],
                url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                zoom: 13,
                center: [-34.9187, -57.956],
            }
        },
        
        beforeCreate(){
            axios.get(API_URL + '/api/centros/').then((res) => {
                this.centros.push(res["data"]["datos"])
                this.centros = this.centros.flat()
                for (let page = 2; page <= res["data"]["total"]; page++) {
                    axios.get(API_URL + '/api/centros/?page=' + page).then((next_few) => {
                        this.centros.push(next_few["data"]["datos"])
                    })
                }
            })
            
        }
    }

</script>