$(document).ready(function () {
    // Maneja el clic en el botón de enviar
    $('.indicaciones').on('click', function() {
        // Obtiene el valor de data-dato
        var dato = $(this).data('dato');
        console.log('Botón clickeado');
        // Realiza una solicitud AJAX a la ruta '/Indicaciones'
        $.ajax({
            type: 'POST',
            url: '/indicaciones',
            data: { dato: dato }, // Enviar dato al servidor
            success: function (data) {
                // Verifica si se realizó una infracción y muestra el modal
                if (data.infraccion) {
                    $('#input-ingreso-id').val(data.dato);
                    $('#flash-message').html('<div class="alert alert-success">' + data.flash_message + '</div>');
                    $('#myCom-Corres').modal('show');
                }
            },
            error: function (error) {
                console.log('Error: ', error);
            }
        });
    });
  });