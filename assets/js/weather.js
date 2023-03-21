"use strict";

const api_key = ""
const city = "";
const url = `https://api.openweathermap.org/data/2.5/forecast?q=${city}&appid=${api_key}`;

document.getElementById("curr_loc").innerHTML = city;

fetch(url)
  .then(response => response.json())
  .then(data => {
    console.log(data);
    // access weather data here
    let date = new Date().toLocaleDateString();
    document.getElementById("curr_date").innerHTML = date;

    document.getElementById("curr_weather").innerHTML = data.list[0].weather[0].description;

    let celcius = parseFloat(data.list[0].main.temp) - 273.15;
    document.getElementById("curr_temperature").innerHTML = celcius.toFixed(1) + "°C";

    if (data.list[0].hasOwnProperty("rain")) {
      const rainVolume = data.list[0].rain["3h"]; // precipitation volume in the last hour in mm
      document.getElementById("curr_precipitation").innerHTML = "Rain precipitation: " + rainVolume;
    }
    else if (data.list[0].hasOwnProperty("snow")) {
      const snowVolume = data.list[0].snow["3h"]; // snow volume in the last hour in mm
      document.getElementById("curr_precipitation").innerHTML = "Snow precipitation: " + snowVolume;
    }
    else {
      document.getElementById("curr_precipitation").innerHTML = "No Precipitation";
    }

    let timestamp = new Date().toLocaleString();
    document.getElementById("timestampweather").innerHTML = timestamp;
  })
  .catch(error => {
    console.log(error);
  });