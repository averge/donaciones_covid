<template>
    <div id="app">
        <div class="container">
            <h2 class="display-4">Estadisticas</h2>
            <h2>Cantidad de centros por tipo</h2>
            

            <div class="container">
                <div v-if="dataCentrosPorTipo.rows.length == 0" >
                    <br>
                    <h5> No hay informacion para mostrar</h5>
                    <br>
                </div>
                <div v-else >
                    <p class="cust-subtitle">Solo se muestran tipos que tienen al menos un centro</p>
                    <ve-pie
                        :data="dataCentrosPorTipo"
                        :settings="settingsPieChart"
                    >
                    </ve-pie>
                </div>
            </div>
            <br>
            <br>
            <h3>Horarios mas solicitados</h3>
            <div class="container">
                <div v-if="dataHorariosSolicitados.rows.length == 0">
                    <br>
                    <h5>No hay informacion para mostrar</h5>
                    <br>
                </div>
                <div v-else>
                    <p class="cust-subtitle">Solo se muestran los horarios que tienen al menos un turno</p>
                    <ve-histogram
                        :data="dataHorariosSolicitados"
                        :settings="settingsHistogramChart"
                    ></ve-histogram>
                    
                    
                </div>
            </div>
            <br>
            <br>
            <h3>Cantidad de centros por municipio</h3>
            <div class="container">
                <div v-if="dataCentrosPorMuni.rows.length == 0" >
                    <br>
                    <h5> No hay informacion para mostrar</h5>
                    <br>
                </div>
                <div v-else >
                    <p class="cust-subtitle">Solo se muestran municipios donde hay al menos un centro</p>
                    <ve-pie 
                        :data="dataCentrosPorMuni"
                        :settings="settingsPieChart"
                    ></ve-pie>
                    
                </div>
            </div>
        </div>
    </div>
</template>
<style scoped>
    .cust-subtitle {
        font-size: 14px;
        color: gray
    }

</style>
<script>
    import VeHistogram from 'v-charts/lib/histogram.common.js'
    import VePie from 'v-charts/lib/pie.common.js'
    import axios from 'axios'
    import { MUNICIPIOS_URL, API_URL } from '@/store'

    export default {
        name: 'Estadisticas',
        components: { VeHistogram, VePie },
        data: function (){
            return {
                settingsPieChart:{
                    selectedMode: 'multiple',
                    radius: 120,
                },
                dataCentrosPorTipo: {
                    columns: ['Tipo' ,'Cantidad'],
                    rows: []
                },
                dataCentrosPorMuni: {
                    columns: ['Municipio', 'Cantidad'],
                    rows: []
                },
                dataHorariosSolicitados: {
                    columns: ['Hora', 'Cantidad'],
                    rows: []
                },
                settingsHistogramChart: {
                    digit: 2
                },
            }

        },
        beforeCreate: function () {
            var munis_api
            munis_api = {}
            axios.get(MUNICIPIOS_URL).then((res_mun) => {
                var towns = res_mun.data["data"]["Town"]
                for(let key in Object.keys(towns)) {
                    if(towns[key]) {
                        munis_api[towns[key]['id']] = towns[key]['name']
                    }
                }
                axios.get(API_URL + "/api/estadisticas/cantidad_municipios").then((res) => {
                    res.data["datos"].forEach( item => {
                        this.dataCentrosPorMuni.rows.push(
                            {
                                'Municipio': munis_api[item['municipio']],
                                'Cantidad': item['cantidad']
                            }
                        )
                    })
                })
            })
            axios.get(API_URL + "/api/estadisticas/tipos_centros").then((res) => {
                res.data["datos"].forEach(item => {
                    item['Tipo'] = item['Tipo'].replaceAll('_', ' ')
                    this.dataCentrosPorTipo.rows.push(item)  
                })
            })
            axios.get(API_URL + "/api/estadisticas/solicitud_horarios").then((res) => {
                res.data['datos'].forEach(item => {
                    this.dataHorariosSolicitados.rows.push(item)
                })
            })
        },
    }
</script>
