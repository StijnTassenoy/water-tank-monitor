function updateValues() {
    fetch("/distance")
        .then(response => response.json())
        .then(values => {
            document.getElementById("fill").innerHTML = values.fill;
            document.getElementById("percentage").innerHTML = values.percentage;
            document.getElementById("tank_progress").style.width = values.percentage + "%";
            console.log("Distance: " + values.distance + " Fill: " + values.fill + " Percentage: " + values.percentage)

            let timestamp = new Date().toLocaleString();
            document.getElementById("timestamp").innerHTML = timestamp;
        })
        .catch(error => {
            console.error(error);
        });
}
setInterval(updateValues, 5000);