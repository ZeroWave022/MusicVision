var baseURL = document.location.origin;

/**
 * Get tracks from the MusicVision API
 * @param {string} timeFrame "long_term", "medium_term" or "short_term"
 * @param {number} limit The number of tracks to get
 * @returns {Promise<Array>} The JSON returned by the API
 */
async function getTracks(timeFrame, limit) {
    let res = await fetch(
        `${baseURL}/api/top/tracks?time_frame=${timeFrame}&limit=${limit}`,
        {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    return res.json();
}

/**
 * Get artists from the MusicVision API
 * @param {string} timeFrame "long_term", "medium_term" or "short_term"
 * @param {number} limit The number of artists to get
 * @returns {Promise<Array>} The JSON returned by the API
 */
async function getArtists(timeFrame, limit) {
    let res = await fetch(
        `${baseURL}/api/top/artists?time_frame=${timeFrame}&limit=${limit}`,
        {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    );

    return res.json();
}

async function createChart(canvas, items) {
    // Create datasets
    const datasets = new Array();
    for (const item of items) {
        datasets.push({
            label: item.name,
            data: item.popularities
        });
    }

    return new Chart(canvas, {
        type: "line",
        data: {
            labels: items[0].timestamps,
            datasets: datasets,
            tension: 1
        },
        options: {
            scales: {
                y: {
                    beginAtZero: false,
                },
            },
        },
    });
}

async function updateChart(type, timeFrame, limit) {
    if (type == "artists") {
        const items = await getArtists(timeFrame, limit);
        artistsChart.destroy();
        artistsChart = await createChart(artistsCanvas, items);
    }
    else if (type == "tracks") {
        const items = await getTracks(timeFrame, limit);
        tracksChart.destroy();
        tracksChart = await createChart(tracksCanvas, items);
    }
        
}

// Global HTMLElements which are canvases which will be reused
var artistsCanvas = document.getElementById("artists-chart");
var tracksCanvas = document.getElementById("tracks-chart");

// Global charts to modify when new data should be presented
var tracksChart;
var artistsChart;

// Initialize charts with default settings
(async () => {
    const trackItems = await getTracks("medium_term", 5);
    const artistItems = await getArtists("medium_term", 5);
    tracksChart = await createChart(tracksCanvas, trackItems);
    artistsChart = await createChart(artistsCanvas, artistItems);
})();
