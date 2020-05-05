function GetURL(keys, values) {
    txt = "?";
    for (i = 0, len = keys.length; i < len; i++) {
        txt += keys[i] + "=" + values[i] + "&";
    }
    return txt.substring(0, txt.length - 1);
}
function UpdateBookalbeInfo() {
    const urlParams = new URLSearchParams(window.location.search);
    const name = urlParams.get('name');
    const id = urlParams.get('id');
    const bookable_id = urlParams.get('bookable_id');
    $.ajax({
        url: "http://localhost:5000/api/users/" + id + "/" + "my_bookables/" + bookable_id + "/",
        headers: { 'Access-Control-Allow-Origin': '*' },
        success: function (body, status, jqxhr) {
            $("#name_input").val(body.name);
            $("#detail_input").val(body.details);
        },
        error: function (jqxhr, type, error) {
            console.log("ERROR (" + type + ") - " + error);
        }
    });
}

$(document).ready(function () {
    UpdateBookalbeInfo();
    $("#cancel_btn").click(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        const bookable_id = urlParams.get('bookable_id');

        window.location = "./my_bookable_detail.html" + GetURL(["id", "name", "bookable_id"], [id, name, bookable_id]);

    });
    $("#save_btn").click(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        const bookable_id = urlParams.get('bookable_id');
        var data = { "name": $("#name_input").val(), "details": $("#detail_input").val() };
        $.ajax({
            url: "http://localhost:5000/api/users/" + id + "/" + "my_bookables/" + bookable_id + "/",
            type: "PUT",
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            headers: { 'Access-Control-Allow-Origin': '*' },
            success: function (body, status, jqxhr) {
                window.location = "./my_bookable_detail.html" + GetURL(["id", "name", "bookable_id"], [id, name, bookable_id]);
            },
            error: function (jqxhr, type, error) {
                console.log("ERROR (" + type + ") - " + error);
            }
        });
    });
});