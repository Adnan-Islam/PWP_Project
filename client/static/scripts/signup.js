
function GetURL(keys, values) {
    txt = "?";
    for (i = 0, len = keys.length; i < len; i++) {
        txt += keys[i] + "=" + values[i] + "&";
    }
    return txt.substring(0, txt.length - 1);
}
$(document).ready(function () {

    $("#sign_up_btn").click(function () {
        var data = { "name": $("#name").val() };
        console.log(JSON.stringify(data));
        $.ajax({
            url: "http://localhost:5000/api/users/",
            type: "POST",
            data: JSON.stringify(data),
            contentType: "application/vnd.mason+json; charset=utf-8",
            dataType: "json",
            headers: { 'Access-Control-Allow-Origin': '*' },
            success: function (body, status, jqxhr) {
                window.location = "../html/MyProfile.html" + GetURL(["id", "name"], [body.id, $("#name").val()]);

            },
            error: function (jqxhr, type, error) {
                console.log("ERROR (" + type + ") - " + error);
            }
        });

    });
});