const studentCount = document.getElementById("student-count");
const cameraStatus = document.getElementById("camera-status");
const cameraFeed = document.getElementById("camera-feed");
const feedMessage = document.getElementById("feed-message");
const countUrl = document.body.dataset.countUrl;

cameraFeed.addEventListener("load", () => {
    feedMessage.hidden = true;
});

cameraFeed.addEventListener("error", () => {
    feedMessage.textContent = "Could not load the camera feed.";
    feedMessage.hidden = false;
});

async function updateDashboard() {
    try {
        const response = await fetch(countUrl);
        if (!response.ok) {
            throw new Error(`Count request failed: ${response.status}`);
        }

        const data = await response.json();
        studentCount.textContent = data.count;
        cameraStatus.textContent = data.status;

        if (data.status !== "Connected") {
            feedMessage.textContent = `Waiting for camera feed (${data.status.toLowerCase()})...`;
            feedMessage.hidden = false;
        } else if (data.frame_ready) {
            feedMessage.hidden = true;
        } else {
            feedMessage.textContent = "Camera connected; waiting for the first frame...";
            feedMessage.hidden = false;
        }
    } catch (error) {
        cameraStatus.textContent = "Disconnected";
        feedMessage.textContent = "Cannot connect to the Flask camera service.";
        feedMessage.hidden = false;
        console.error("Could not update the dashboard:", error);
    }
}

updateDashboard();
setInterval(updateDashboard, 500);
