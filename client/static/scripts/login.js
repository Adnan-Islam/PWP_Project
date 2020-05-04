"user strict";

function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
    $("div.notification").html("<p class='error'>" + msg + "</p>");
}

function getResource(href, renderFunction) {
    $.ajax({
        url: href,
        headers: { 'Access-Control-Allow-Origin': '*' },
        success: renderFunction,
        error: renderError
    });
}

function sensorRow(item) {
    return "<tr><td>" + item.name + "</td></tr>";
}

function renderSensors(body) {
    console.log(body);

    $(".resulttable thead").html(
        "<tr><th>Name</th><th>Model</th><th>Location</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.append(sensorRow(body));
}

function UserCreated() {
    window.location = "../html/profile.html";
}

$(document).ready(function () {


    $("#log_in_btn").click(function () {
        $.ajax({
            url: "http://localhost:5000/api/users/" + $("#username_input").val() + "/",
            headers: { 'Access-Control-Allow-Origin': '*' },
            success: function (body, status, jqxhr) {
                window.location = "../html/myprofile.html" + "?" +  "id=" + body.id + "&name=" + body.name
            },
            error: function (jqxhr, type, error) {
                console.log("ERROR (" + type + ") - " + error);
            }
        });

    });


    $("#sign_up_btn").click(function () {
        window.location = "../html/sign-up.html";

        // var data = { "name": $("#name").val() };
        // console.log(JSON.stringify(data));
        // $.ajax({
        //     url: "http://localhost:5000/api/users/",
        //     type: "POST",
        //     data: JSON.stringify(data),
        //     contentType: "application/json; charset=utf-8",
        //     dataType: "json",
        //     headers: { 'Access-Control-Allow-Origin': '*' },
        //     success: UserCreated,
        //     error: renderError
        // });

    });
});

