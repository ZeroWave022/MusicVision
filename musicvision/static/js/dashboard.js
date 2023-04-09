const icons = {
    play: "circle-play-solid.svg",
    pause: "circle-pause-solid.svg"
}

async function play_button_event() {
    baseURL = document.location.origin;
    let res = await fetch(`${baseURL}/api/toggle_player`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
    });

    resContent = await res.json();

    if (resContent.status != "success") {
        return;
    }

    image = document.querySelector("#track-info img");
    srcSplit = image.src.split("/");

    if (resContent.isPlaying) {
        srcSplit[srcSplit.length - 1] = icons.pause;
    }
    else {
        srcSplit[srcSplit.length - 1] = icons.play;
    }

    image.src = srcSplit.join("/");
}
