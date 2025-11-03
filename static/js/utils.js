function BuildUrl(path) {
    let protocol = window.location.protocol;
    let hostname = window.location.hostname;
    let port = window.location.port;
    let fullUrl = protocol + '//' + hostname + ":" + port + "/" + path;
    return fullUrl
}

