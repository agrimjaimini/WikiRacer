var socket = io.connect("https://" + window.location.hostname + ':' + location.port);

socket.on('path_update', function(data) {
    var pathLinks = data.path.map(function(page, index) {
        return '<a href="' + data.links[index] + '" target="_blank" style="color: #2aa9e0;">' + page + '</a>';
    });
    document.getElementById('path').innerHTML = 'This is a new path! Current Path: ' + pathLinks.join(' → ');
});

socket.on('new_link', function(data) {
    const currentLink = document.getElementById('current_link');
    currentLink.style.display = 'block';
    currentLink.innerHTML = 'Currently traversing: ' + data.link;
});

socket.on('search_complete', function(data) {
    document.getElementById('spinner').style.display = 'none';
    document.getElementById('startButton').disabled = false;

    var alerts = document.getElementsByClassName('alert');
    for (var i = 0; i < alerts.length; i++) {
        alerts[i].style.display = 'none';
    }

    var pathLinks = data.path.map(function(page, index) {
        return '<a href="' + data.links[index] + '" target="_blank" style="color: #2aa9e0;">' + page + '</a>';
    });

    document.getElementById('current_link').style.display = 'none';
    document.getElementById('path').innerHTML = 
        'Search Complete! Final Path: ' + pathLinks.join(' → ') + ' found on ' + data.timestamp;

    setTimeout(function() {
        document.getElementById('path').innerHTML = '';
    }, 300000);
});

socket.on('search_exists', function(data) {
    document.getElementById('spinner').style.display = 'none';
    document.getElementById('startButton').disabled = false;

    var alerts = document.getElementsByClassName('alert');
    for (var i = 0; i < alerts.length; i++) {
        alerts[i].style.display = 'none';
    }

    var pathLinks = data.path.map(function(page, index) {
        return '<a href="' + data.links[index] + '" target="_blank" style="color: #2aa9e0;">' + page + '</a>';
    });

    document.getElementById('path').innerHTML = 
        'This search already exists! Path: ' + pathLinks.join(' → ') + ' found on ' + data.timestamp;

    setTimeout(function() {
        document.getElementById('path').innerHTML = '';
    }, 300000);
});

socket.on('size_warning', function(data) {
    const errorElement = document.getElementById('error');
    errorElement.style.display = 'block';
    errorElement.innerHTML = 'Oh no! Your optimal path includes a page with >' + data.size + ' links.';
    document.getElementById('startButton').disabled = false;
});

document.getElementById('startButton').addEventListener('click', function() {
    const startPage = document.getElementById('startPage').value;
    const endPage = document.getElementById('endPage').value;

    if (startPage.trim() !== '' && endPage.trim() !== '') {
        document.getElementById('path').innerHTML = '';
        document.getElementById('error').style.display = 'none';
        document.getElementById('spinner').style.display = 'block';
        document.getElementById('startButton').disabled = true;

        socket.emit('start_search', { start: startPage, end: endPage });
    } else {
        const errorElement = document.getElementById('error');
        errorElement.style.display = 'block';
        errorElement.innerHTML = 'Please enter both a start and an end page.';
    }
});

const forms = document.getElementsByClassName('form-group');
for (let i = 0; i < forms.length; i++) {
    forms[i].addEventListener('input', function () {
        const inputField = this;
        socket.emit('link_check', { title: inputField.value });

        socket.on('link_check_response', function (data) {
            if (data.exists) {
                inputField.style.outline = '2px solid blue';
                document.getElementById('startButton').disabled = false;
            } else {
                inputField.style.outline = '2px solid red';
                document.getElementById('startButton').disabled = true;
            }
        });
    });
}
