function close_navbar(nav_box, spans) {
    nav_box.style.display = "none";
    for(let i = 0; i < spans.length; i++) {
        spans[i].style.background = "white";
    }
}

function setEventListeners() {
    // Listener de la caja de error/exito al validar formularios
    var alert_box = document.querySelector(".alert");
    if(alert_box) {
        alert_box.addEventListener("click", function() {
            alert_box.remove();
        });
    }

    // Listener del menu
    var menu = document.querySelector(".hamburguer-menu");
    var nav_box = document.querySelector(".nav-box");
    var spans = menu.querySelectorAll("span");
    var content = document.querySelector(".content");
    menu.addEventListener("click", function() {
        if(nav_box.offsetWidth == 0 && nav_box.offsetHeight == 0) {
            for(let i = 0; i < spans.length; i++) {
                spans[i].style.background = "#cdcdcd";
            }
            nav_box.style.display = "block";
        } else {
            close_navbar(nav_box, spans);
        }
    });
    content.addEventListener("click", function() {
        close_navbar(nav_box, spans);
    });
}

window.onload = function() {
    setEventListeners();
};