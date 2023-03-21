"use strict";

console.log(percentage)

function updateValues() {
    fetch("http://192.168.0.18/distance")
        .then(response => response.json())
        .then(values => {
            document.getElementById("fill").innerHTML = values.fill;
            document.getElementById("percentage").innerHTML = values.percentage;
            document.getElementById("tank_progress").style.width = values.percentage + "%";
            console.log("Distance: " + values.distance + " Fill: " + values.fill + " Percentage: " + values.percentage)

            let timestamp = new Date().toLocaleString();
            document.getElementById("timestamptank").innerHTML = timestamp;
        })
        .catch(error => {
            console.error(error);
        });
}
setInterval(updateValues, 5000);


//line
var ctxL = document.getElementById("historyChart").getContext("2d");
var myLineChart = new Chart(ctxL, {
  type: "line",
  data: {
    labels: ["1609459314", "1609459316", "1609459387"],
    datasets: [
    {
      fill: 'origin',
      label: "Water Level History",
      data: [65, percentage, 70],
      backgroundColor: [
        'rgba(240, 203, 55, .2)',
      ],
      borderColor: [
        'rgba(240, 203, 55, .7)',
      ],
      borderWidth: 2
    }
    ]
  },
  options: {
    responsive: true
  }
});