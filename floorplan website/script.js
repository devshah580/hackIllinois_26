const { createClient } = supabase;

// Supabase credentials
const SUPABASE_URL = "https://upsqvxtvlvxyuimngxil.supabase.co";
const SUPABASE_KEY = "sb_publishable_KSHPacBUw328_e-hVpgboA_OdLOcGhg";

const supabaseClient = createClient(SUPABASE_URL, SUPABASE_KEY);

// DOM elements
const imgEl = document.getElementById("floorplan");
const canvas = document.getElementById("overlay");
const ctx = canvas.getContext("2d");
const status = document.getElementById("status");
const mapContainer = document.getElementById("map-container");

// Global state
let images = []; // will store public URLs of floorplans
let currentIndex = 0;
let currentMode = null; // 'restroom', 'water', or null
let locations = [];

// Enable zoom & pan
panzoom(mapContainer, { maxZoom: 3, minZoom: 0.5 });

// Attach functions to window for HTML buttons
window.nextImage = nextImage;
window.prevImage = prevImage;
window.setMode = setMode;

// ===========================
// Initialize images
// ===========================
async function loadImages() {
    const { data, error } = await supabaseClient
        .storage
        .from('floorplans')
        .list('', { limit: 100 });

    if (error) {
        console.error("List error:", error);
        status.textContent = "Error loading floorplans.";
        return;
    }

    console.log("ROOT:", data);

    images = data
        .filter(file => file.name.endsWith(".png"))
        .map(file =>
            supabaseClient
                .storage
                .from('floorplans')
                .getPublicUrl(file.name)
                .data.publicUrl
        );

    images.sort(); // keeps floors ordered alphabetically

    console.log("Generated URLs:", images);

    if (images.length === 0) {
        status.textContent = "No images found.";
        return;
    }

    currentIndex = 0;
    loadFloorplan(images[currentIndex]);
}
// ===========================
// Load a single floorplan & its markers
// ===========================
async function loadFloorplan(url) {
    if (!url) {
        console.error("Invalid URL:", url);
        return;
    }
    imgEl.src = url;
    status.textContent = `Showing ${currentIndex + 1} of ${images.length}`;

    const filename = decodeURIComponent(url.split('/').pop());

    try {
        const { data, error } = await supabaseClient
            .from('locations')
            .select('*')
            .eq('floorplan_name', filename);

        if (error) throw error;
        locations = data || [];

    } catch (err) {
        console.error("Error fetching locations:", err);
        locations = [];
    }

    imgEl.onload = drawOverlay;
}

// ===========================
// Draw markers on overlay
// ===========================
function drawOverlay() {
    canvas.width = imgEl.clientWidth;
    canvas.height = imgEl.clientHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    locations.forEach(loc => {
        if (currentMode && loc.type !== currentMode) return;

        const x = loc.x * canvas.width;
        const y = loc.y * canvas.height;

        ctx.beginPath();
        ctx.arc(x, y, 10, 0, Math.PI * 2);

        if (loc.type === "restroom") ctx.fillStyle = "red";
        else if (loc.type === "water") ctx.fillStyle = "blue";
        else ctx.fillStyle = "green";

        ctx.fill();
    });
}

// ===========================
// Navigation
// ===========================
function nextImage() {
    if (images.length === 0) return;
    currentIndex = (currentIndex + 1) % images.length;
    loadFloorplan(images[currentIndex]);
}

function prevImage() {
    if (images.length === 0) return;
    currentIndex = (currentIndex - 1 + images.length) % images.length;
    loadFloorplan(images[currentIndex]);
}

// ===========================
// Set marker filter mode
// ===========================
function setMode(mode) {
    currentMode = mode; // 'restroom', 'water', or null
    drawOverlay();
}

// ===========================
// Initialize
// ===========================
loadImages();