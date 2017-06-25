var visits = document.getElementById('stats-visits').getContext('2d');

$.getJSON('/rest/stats/', {type: 'all'}, function (data) {
    var chart = new Chart(visits, {
        // The type of chart we want to create
        type: 'line',
        // The data for our dataset
        data: {
            labels: data.visits.labels,
            datasets: [{
                label: "Liczba wizyt",
                backgroundColor: 'rgb(255, 99, 132)',
                borderColor: 'rgb(255, 99, 132)',
                data: data.visits.data,
            }]
        },
        // Configuration options go here
        options: {}
    });
});