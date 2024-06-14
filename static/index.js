document.getElementById('image-gen-btn').addEventListener('click', function() {
    const prompt = document.getElementById('promptInput').value;
    const img = document.getElementById('generatedImage');
    const btn = document.getElementById('image-gen-btn');
    const loading = document.getElementById('loading'); // Get loading element
    
    btn.disabled = true;
    btn.style.display = 'none';
    loading.style.display = 'inline-block'; // Show loading spinner

    fetch('/image', {
        method: 'POST',
        body: JSON.stringify({ prompt: prompt }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);
        img.src = url;
        img.style.display = 'block';
        btn.disabled = false;
        loading.style.display = 'none'; // Hide loading spinner
        btn.style.display = 'inline-block';
    })
    .catch(error => {
        console.error('Error:', error);
        btn.disabled = false;
        loading.style.display = 'none'; // Hide loading spinner in case of error
        btn.style.display = 'inline-block';
    });
});
