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
            $("h5").html("My Bookable Name:" + body.name);
            $("#bookable_table").html("<tr>" +
                "<th> Description </th>" +
                "</tr>" +
                "<tr style=font-size: 20px>" +
                "<td><h4>" + body.details + "</h4></td>" +
                "</tr>");
        },
        error: function (jqxhr, type, error) {
            console.log("ERROR (" + type + ") - " + error);
        }
    });
}

$(document).ready(function () {
    UpdateBookalbeInfo();
    $("#back_to_my_bookable_btn").click(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        window.location = "./mybookables.html" + GetURL(["id", "name"], [id, name]);

    });
});