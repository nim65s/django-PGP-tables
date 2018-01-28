var ctx = document.getElementById("myChart");

var myChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: [{% for label, count in object.algo_stats %}
            "{{ label }}",
            {% endfor %}
        ],
            datasets: [{
                data: [{% for label, count in object.algo_stats %} {{ count }},{% endfor %}],
                backgroundColor: ['#803690', '#00ADF9', '#DCDCDC', '#46BFBD', '#FDB45C', '#949FB1', '#4D5360'],
                hoverBackgroundColor: ['#803690', '#00ADF9', '#DCDCDC', '#46BFBD', '#FDB45C', '#949FB1', '#4D5360']
            }]
    },
    options: {}
});
