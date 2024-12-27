function cargarPagina(pagina) {
    // Simula la carga de contenido dinámico usando AJAX
    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            document.getElementById('contenido').innerHTML = xhr.responseText;
        }
    };
    xhr.open('GET', pagina + '.html', true);
    xhr.send();
}


// Función para mostrar/ocultar el texto adicional y la imagen para cada conclusión
function toggleConclusion(conclusionId) {
    var textPart = document.getElementById("text" + conclusionId);
    var toggleButton = document.querySelector("#conclusion" + conclusionId + " .toggle-button");
    var imageContainer = document.getElementById("image" + conclusionId);

    if (textPart.style.display === "none" || textPart.style.display === "") {
        textPart.style.display = "block";
        toggleButton.innerHTML = "-"; // Cambia el texto del botón a "-"
        imageContainer.style.display = "block"; // Muestra la imagen
    } else {
        textPart.style.display = "none";
        toggleButton.innerHTML = "+"; // Cambia el texto del botón a "+"
        imageContainer.style.display = "none"; // Oculta la imagen
    }
}

