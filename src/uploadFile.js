function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select a video file to upload.');
        return;
    }

    const formData = new FormData();
    formData.append('videoFile', file);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', 'YOUR_API_ENDPOINT_URL', true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                alert('Video uploaded successfully!');
            } else {
                alert('Error uploading the video. Please try again later.');
            }
        }
    };
    xhr.send(formData);
}
