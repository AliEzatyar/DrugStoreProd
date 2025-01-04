document.addEventListener('DOMContentLoaded', (e) => {
    document.getElementById('dialog').showModal()


    // qr reading
    const cameraSelection = document.getElementById('cameraSelection')
    const qrCodeScanner = new Html5Qrcode("reader")

    // Populate camera options
    Html5Qrcode.getCameras()
        .then((cameras) => {
            if (cameras && cameras.length) {
                cameras.forEach((camera, index) => {
                    const option = document.createElement('option')
                    option.value = camera.id
                    option.text = camera.label || `Camera ${index + 1}`
                    cameraSelection.appendChild(option)
                })
                var selected_camera = cameras[0];
                if (cameras.length >1){
                    selected_camera = cameras[2];
                }
                // Start with the first camera by default
                qrCodeScanner.start(
                    selected_camera.id,
                    {
                        fps: 10,
                        qrbox: { width: 250, height: 250 }
                    },
                    (decodedText, decodedResult) => {
                        const drug_id = decodedText.split("_", 1)
                        const url = window.location.protocol + "//" + window.location.host + `/sell/${drug_id}`
                        window.location.href = url
                    }
                )
            } else {
                console.error('No cameras found!')
            }
        })
        .catch((err) => {
            console.error('Error getting cameras:', err)
        })

    // Handle camera selection change
    cameraSelection.addEventListener('change', () => {
        const selectedCameraId = cameraSelection.value
        qrCodeScanner.stop().then(() => {
            qrCodeScanner.start(
                selectedCameraId,
                {
                    fps: 10,
                    qrbox: { width: 250, height: 250 }
                },
                (decodedText, decodedResult) => {
                    // redirecting to main selling page
                    const drug_id = decodedText.split("_", 1)
                    const url = window.location.protocol + "//" + window.location.host + `/sell/${drug_id}`
                    window.location.href = url
                }
            )
        })
    })
})