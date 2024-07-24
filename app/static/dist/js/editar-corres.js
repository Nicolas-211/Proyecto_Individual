$(document).ready(function () {
    // Maneja el clic en el botón de enviar
    $('.editarCorres').on('click', function() {
        // Obtiene el valor de data-dato
        var dato = $(this).data('dato');
        var fechaingreso = $(this).data('fechaingreso');
        var documento = $(this).data('documento');
        var rit = $(this).data('rit');
        var origen = $(this).data('origen');
        var distribución = $(this).data('distribución');

        
        // Realiza una solicitud AJAX a la ruta '/Indicaciones'
        $.ajax({
            type: 'POST',
            url: '/editarCorres',
            data: { dato: dato, fechaingreso: fechaingreso,documento:documento,rit:rit,origen:origen,distribución:distribución}, // Enviar dato al servidor
            success: function (data) {
                // Verifica si se realizó una infracción y muestra el modal
                if (data.infraccion) {
                    console.log(data.flash_message)
                    $('#input-corres-id').val(data.dato);
                    $('#input-corres-fecha-ingreso').val(data.fechaingreso);
                    $('#input-corres-numero-documento').val(data.documento);
                    $('#input-corres-RIT').val(data.rit);
                    $('#input-corres-origen').val(data.origen);
                    $('#input-corres-distribución').val(data.distribución);
                    $('#flash-message').html('<div class="alert alert-success">' + data.flash_message + '</div>');
                    $('#myEdit').modal('show');
                }
            },
            error: function (error) {
                console.log('Error: ', error);
            }
        });
    });
  });