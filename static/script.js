document.querySelector('.btn-search').addEventListener('click', function () {
    let searchTerm = document.querySelector('input[type="text"]').value;

    if (searchTerm) {
        // Fetch the movie posters from TMDB API
        fetch(`https://api.themoviedb.org/3/search/movie?api_key=66b309a9a99a994c040c6dca2a34d606&query=${searchTerm}`)
            .then(response => response.json())
            .then(data => {
                // Display the movie posters in the scroll container
                let scrollContainer = document.querySelector('.scroll-container');
                scrollContainer.innerHTML = '';

                data.results.forEach(movie => {
                    let img = document.createElement('img');
                    img.src = `https://image.tmdb.org/t/p/w500/${movie.poster_path}`;
                    img.alt = movie.title;
                    scrollContainer.appendChild(img);
                });
            });
    }
});

document.querySelector('.contact-form').addEventListener('submit', function (event) {
    event.preventDefault();

    // Retrieve the form data
    let formData = new FormData(event.target);

    // Send the form data to the server
    fetch('your_server_endpoint', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Message sent successfully');
            } else {
                alert('Error sending message');
            }
        });
});
