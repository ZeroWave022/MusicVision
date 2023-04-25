/**
 * Get an artist from the MusicVision API
 * @param {string} timeFrame The time frame to get
 * @param {string} id The id to get
 * @returns {Promise<object>} The JSON returned by the API
 */
async function getArtist(id, time_frame) {
    const URL = `${baseURL}/api/artist/${id}?time_frame=${time_frame}`

    let res = await fetch(
        URL,
        {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    return res.json();
}

async function updateArtistChart(time_frame) {
    if (chart) chart.destroy();

    const pathname = document.location.pathname;
    
    // Get the id of the item from the pathname
    const id = pathname.split("/").slice(-1)[0];

    let artist = await getArtist(id, time_frame);

    if (!artist.chart_data) {
        text.style.display = "block";
    } else {
        text.style.display = "none";
    }

    chart = new Chart(canvas, {
        type: "line",
        data: {
            labels: artist.chart_data.timestamps,
            datasets: [{
                label: `${artist.name} - ${timeFrameNames[artist.chart_data.time_frame]}`,
                data: artist.chart_data.popularities
            }],
            tension: 0.5
        }
    });
}

var baseURL = document.location.origin;
const timeFrameNames = {
    short_term: "Last 4 weeks",
    medium_term: "Last 6 months",
    long_term: "All time"
}

var text = document.getElementById("info-text");
var canvas = document.getElementById("artist-chart");
var chart;

updateArtistChart("long_term");
