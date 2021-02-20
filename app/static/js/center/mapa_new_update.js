let map;
let marker;

function mapClickHandler(e) {
    addMarker(e.latlng);
}

function addMarker( {lat, lng }) {
    if (marker) marker.remove();
    marker = L.marker([lat, lng]).addTo(map);
}

function initializeMap(selector) {
    var centro;
    if ( 
        (document.getElementById('lat').value)
        ||
        (document.getElementById('lng').value)
        ){
            centro = [parseFloat(document.getElementById('lat').value), parseFloat(document.getElementById('lng').value)]        
    }else{
        centro = [-34.9187, -57.956]

    }

    map = L.map(selector).setView(centro, 13);
    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
		maxZoom: 18,
		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
			'<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
			'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
		id: 'mapbox/streets-v11',
		tileSize: 512,
		zoomOffset: -1
    }).addTo(map);
    map.on('click', mapClickHandler);
    
    if (( (document.getElementById('lat').value)) && ( (document.getElementById('lng').value))){    
        addMarker( {lat:(parseFloat(document.getElementById('lat').value)), lng:(parseFloat(document.getElementById('lng').value))} );
    }
}

const submitHandler = (event) => {
    if (!marker) {
        event.preventDefault();
        alert('Debe seleccionar una ubicacion en el mapa');
    }else{
        latlng = marker.getLatLng();
        document.getElementById('lat').setAttribute('value', latlng.lat);
        document.getElementById('lng').setAttribute('value', latlng.lng);
    }
}

initializeMap('mapid');


