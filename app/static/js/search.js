// Enviar el formulario al apretar la lupa de busqueda
lupa = document.querySelector("#search-lupa");
lupa.addEventListener("click", function() {
    document.querySelector("#search-form").submit();
});

more = document.querySelector("#more-options");
more_box = document.querySelector("#more-options-box");
more.addEventListener("click", function() {
    if(more_box.offsetWidth == 0 && more_box.offsetHeight == 0) {
        more_box.style.display = "block";
    } else {
        more_box.style.display = "none";
    }
})