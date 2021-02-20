municipios = document.querySelector("#municipios");
fetch("https://api-referencias.proyecto2020.linti.unlp.edu.ar/municipios?per_page=200")
.then(function (response) {
    return response.json();
})
.then(function (json) {
    towns = json["data"]["Town"];
    for(let key of Object.keys(towns)) {
        let option = document.createElement("option");
        option.setAttribute("data-value", towns[key]["id"]);
        option.innerHTML = towns[key]["name"];
        municipios.appendChild(option);
    }
    var muni_value = document.querySelector("#muni").value;
    if(muni_value) {
        for(let key of Object.keys(towns)) {
            if(towns[key]["id"] == muni_value) {
                document.querySelector("input[list]").value = towns[key]["name"];
            }
        }
    }
});

document.querySelector('input[list]').addEventListener('input', function(e) {
    var input = document.querySelector("input[list]");
    var list = input.getAttribute("list");
    var options = document.querySelectorAll('#' + list + ' option');
    var hiddenInput = document.querySelector('#muni');

    hiddenInput.value = input.value;

    for(var i = 0; i < options.length; i++) {
        var option = options[i];

        if(option.innerText === input.value) {
            hiddenInput.value = option.getAttribute('data-value');
            break;
        }
    }
});