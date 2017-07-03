var visitsCanvas = document.getElementById('stats-visits').getContext('2d');
var doctorsCanvas = document.getElementById('stats-doctors').getContext('2d');
var visitsTimeCanvas = document.getElementById('stats-visits-time').getContext('2d');

$.getJSON('/rest/stats/', {type: 'all'}, function (data) {
    var visits = new Chart(visitsCanvas, {
        // The type of chart we want to create
        type: 'line',
        // The data for our dataset
        data: {
            labels: data.visits.labels,
            datasets: [{
                label: "Liczba wizyt",
                backgroundColor: 'rgba(0,130,198,0.8)',
                borderColor: '#d8e2e7',
                data: data.visits.data,
            }]
        },
        // Configuration options go here
        options: {
            scales: {
                xAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Miesiąc'
                    }
                }]
            }
        }
    });
    var visitsTime = new Chart(visitsTimeCanvas, {
        // The type of chart we want to create
        type: 'line',
        // The data for our dataset
        data: {
            labels: data.visits_time.labels,
            datasets: [{
                label: "Liczba wizyt",
                backgroundColor: 'rgba(0,130,198,0.8)',
                borderColor: '#d8e2e7',
                data: data.visits_time.data
            }]
        },
        // Configuration options go here
        options: {
            scales: {
                xAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Godzina'
                    }
                }]
            }
        }
    });
        var visits = new Chart(doctorsCanvas, {
        // The type of chart we want to create
        type: 'bar',
        // The data for our dataset
        data: {
            labels: data.doctors.labels,
            datasets: [{
                label: "Liczba wizyt",
                backgroundColor: 'rgba(0,130,198,0.8)',
                borderColor: '#d8e2e7',
                data: data.visits.data,
            }]
        },
        // Configuration options go here
        options: {
            scales: {
                xAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Lekarz'
                    }
                }]
            }
        }
    });
});