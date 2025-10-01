function nocodealert(msg, type='success', timer=2000) {
    Swal.fire({
        text: msg,
        icon: type,           
        timer: timer, 
        showConfirmButton: false,
        timerProgressBar: true,
        position: 'top-end'
    });
}
function nocodeConfirm(message = "Are you sure?", confirmText = "Yes", cancelText = "No") {
    return Swal.fire({
        text: message,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: confirmText,
        cancelButtonText: cancelText,
        reverseButtons: true,
        focusCancel: true,
        position: 'top-end'
    }).then((result) => result.isConfirmed);
}
