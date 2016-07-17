/*
*/

function parseUrl(url) {
    var a = document.createElement('a');
    a.href = url;
    return a;
}

function getMapId() {
    var url = parseUrl(window.location);
    return url.pathname.match(/\/m\/([^\/&?]+)/)[1];
}

MAP_BASE_URL = '//s3.amazonaws.com/quarrius-output/worlds/';
MAP_TILE_SUFFIX = '/region/r.{x}.{y}.mca.png'

var map = L.map('map_view', {
    center: [0.0, 0.0],
    minZoom: 0,
    maxZoom: 0,
    crs: L.CRS.Simple,
}).setView([0.0, 0.0], 0);

L.tileLayer(MAP_BASE_URL + getMapId() + MAP_TILE_SUFFIX, {
    tileSize: 512,
    maxNativeZoom: 0,
    continuousWorld: true,
    // noWrap: true,
}).addTo(map);
