function confirmarEliminacion(id, nombre) {
    Swal.fire({
        title: '¿Estás seguro?',
        text: `Eliminarás a ${nombre}. Esta acción no se puede deshacer.`,
        icon: 'warning',
        showCancelButton: true,
        confirmColor: '#dc2626',
        cancelColor: '#6b7280',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/empleados/eliminar/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire('¡Eliminado!', data.message, 'success').then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire('Error', data.message, 'error');
                }
            })
            .catch(() => {
                Swal.fire('Error', 'No se pudo completar la solicitud.', 'error');
            });
        }
    });
}