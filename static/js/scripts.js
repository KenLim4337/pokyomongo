const MAP_BOUNDS = L.latLngBounds(L.latLng(42.697577, 74.413841), L.latLng(43.023726, 74.795853));

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(document).ready(function() {
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
        
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});

function getSessionCaptured() {
    if (sessionStorage.getItem("captured") === null) {
        sessionStorage.setItem("captured", "[]");
    }

    return JSON.parse(sessionStorage.getItem("captured"));
}

function clearSessionCaptured() {
    sessionStorage.setItem("captured", "[]");
}