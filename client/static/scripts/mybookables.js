function GetURL(keys, values) {
    txt = "?";
    for (i = 0, len = keys.length; i < len; i++) {
        txt += keys[i] + "=" + values[i] + "&";
    }
    return txt.substring(0, txt.length - 1);
}

function GetMyBookables() {
    const urlParams = new URLSearchParams(window.location.search);
    const name = urlParams.get('name');
    const id = urlParams.get('id');
    $.ajax({
        url: "http://localhost:5000/api/users/" + id + "/" + "my_bookables/",
        type: "GET",
        headers: { 'Access-Control-Allow-Origin': '*' },
        success: function (body, status, jqxhr) {
            console.log(body);
            RenderItems(body.items);

        },
        error: function (jqxhr, type, error) {
            console.log("ERROR (" + type + ") - " + error);
        }
    });
}
function RenderItems(items) {
    const urlParams = new URLSearchParams(window.location.search);
    const name = urlParams.get('name');
    const id = urlParams.get('id');
    html = "<tr><th> Name </th><th> Description </th></tr>";
    for (let i = 0; i < items.length; i++) {
        html += "<tr>"
            + "<td>" + items[i].name + "</td>"
            + "<td>" + items[i].details + "<a href=../html/my_bookable_detail.html" + GetURL(["id", "name", "bookable_id"], [id, name, items[i].id]) + " target=_parent>"
            + "<button class=table_button id=table_button" + items[i].id + "> details</button></a>"
            + "</td>"
            + "</tr>";
    }
    $("#bookable_table").html(html);
}
$(document).ready(function () {
    GetMyBookables();

    $("#back_to_profile_btn").click(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        window.location = "./myprofile.html" + GetURL(["id", "name"], [id, name]);

    });
    $("#new_bookable_btn").click(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        window.location = "./new_bookable.html" + GetURL(["id", "name"], [id, name]);

    });
});