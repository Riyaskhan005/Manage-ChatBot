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

function nocodeCenterAlert(msg, type = 'success', timer = 2000, callback = null) {
    const contentHtml = `
        <div style="font-size:16px; font-weight:600; line-height:1.2; text-align:center;">
            ${msg}
        </div>
        <div style="margin-top:8px; font-size:14px; color:#6c757d; text-align:center;">
            Please wait...
        </div>
    `;

    Swal.fire({
        html: contentHtml,
        icon: type,
        timer: timer,
        showConfirmButton: false,
        timerProgressBar: true,
        position: 'center'
    }).then(() => {
        if (callback) callback();
    });
}
