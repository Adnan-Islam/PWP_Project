
function UserCreated(body, status) {
    window.location = "../html/MyProfile.html";
}

$(document).ready(function () {

    $("#sign_up_btn").click(function () {
        var data = { "name": $("#name").val() };
        console.log(JSON.stringify(data));
        $.ajax({
            url: "http://localhost:5000/api/users/",
            type: "POST",
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            headers: { 'Access-Control-Allow-Origin': '*' },
            success: UserCreated,
            error: function (jqxhr, type, error) {
                console.log("ERROR (" + type + ") - " + error);
            }
        });

    });
});