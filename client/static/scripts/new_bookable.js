function GetURL(keys, values) {
    txt = "?";
    for (i = 0, len = keys.length; i < len; i++) {
        txt += keys[i] + "=" + values[i] + "&";
    }
    return txt.substring(0, txt.length - 1);
}

$(document).ready(function () {
    $("#save_btn").click(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        var data = { "name": $("#name_input").val(), "details": $("#detail_input").val() };

        $.ajax({
            url: "http://localhost:5000/api/users/" + id + "/my_bookables/",
            type: "POST",
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            headers: { 'Access-Control-Allow-Origin': '*' },
            success: function (status, jqxhr) {
                window.location = "../html/mybookables.html" + GetURL(["id", "name"], [id, name]);

            },
            error: function (jqxhr, type, error) {
                console.log("ERROR (" + type + ") - " + error);
            }
        });
    });

    $("#cancel_btn").click(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        window.location = "../html/mybookables.html" + GetURL(["id", "name"], [id, name]);
    });
});