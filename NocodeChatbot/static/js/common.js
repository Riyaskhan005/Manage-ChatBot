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