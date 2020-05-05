function GetURL(keys, values) {
    txt = "?";
    for (i = 0, len = keys.length; i < len; i++) {
        txt += keys[i] + "=" + values[i] + "&";
    }
    return txt.substring(0, txt.length - 1);
}

function GetAllBookalbes() {
    const urlParams = new URLSearchParams(window.location.search);
    const name = urlParams.get('name');
    const id = urlParams.get('id');
    $.ajax({
        url: "http://localhost:5000/api/users/" + id + "/" + "bookables/",
        type: "GET",
        headers: { 'Access-Control-Allow-Origin': '*' },
        success: function (body, status, jqxhr) {
            RenderItems(body.items);

        },
        error: function (jqxhr, type, error) {
            console.log("ERROR (" + type + ") - " + error);
        }
    });
}

function RenderItems(items) {
    html = "<tr><th> Name </th><th> Description </th></tr>";
    for (let i = 0; i < items.length; i++) {
        html += "<tr>"
            + "<td>" + items[i].name + "</td>"
            + "<td>" + items[i].details + "<a href=./bookable_detail.html target=_parent>"
            + "<button class=table_button id=table_button> details</button></a>"
            + "</td>"
            + "</tr>";
    }
    $("#bookable_table").html(html);
}
$(document).ready(function () {
    GetAllBookalbes();

    $("#back_to_user_btn").click(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        window.location = "./MyProfile.html" + GetURL(["id", "name"], [id, name]);

    });
});