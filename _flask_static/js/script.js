"use strict";

let refreshInterval = 5000;

function updateCurrentTank() {
    fetch("/tank_data")
        .then(response => response.json())
        .then(values => {
            console.log("Distance: " + values.distance + " Fill: " + values.fill + " Percentage: " + values.percentage)

            document.getElementById("fill").innerHTML = values.fill;
            document.getElementById("percentage").innerHTML = values.percentage;
            document.getElementById("tank_progress").style.height = values.percentage + "%";

            let timestamp = new Date().toLocaleString();
            document.getElementById("timestamptank").innerHTML = timestamp;
        })
        .catch(error => {
            console.error(error);
        });
}
setInterval(updateCurrentTank, refreshInterval);


let myLineChart = null; // initialize chart variable

function updateHistoryChart() {
    fetch("/tank_history")
        .then(response => response.json())
        .then(values => {
            console.log(values)

            let ctxL = document.getElementById("historyChart").getContext("2d");

            if (!myLineChart) { // create new chart if it doesn't exist
                myLineChart = new Chart(ctxL, {
                    type: "line",
                    data: {
                        labels: values.timestamp_history,
                        datasets: [{
                            fill: "origin",
                            label: "Water Level History",
                            data: values.percentage_history,
                            backgroundColor: [
                                "rgba(240, 203, 55, .2)",
                            ],
                            borderColor: [
                                "rgba(240, 203, 55, .7)",
                            ],
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            yAxes: [{
                                ticks: {
                                    min: 0,
                                    max: 100,
                                    callback: function(value) {
                                        return value.toString();
                                    }
                                }
                            }]
                        }
                    }
                });
            } else { // update existing chart with new data
                myLineChart.data.labels = values.timestamp_history;
                myLineChart.data.datasets[0].data = values.percentage_history;
                myLineChart.update();
            }
        })
        .catch(error => {
            console.error(error);
        });
}
setInterval(updateHistoryChart, refreshInterval);

