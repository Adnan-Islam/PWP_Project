function UpdateUserInfo(changedname = "") {
    const urlParams = new URLSearchParams(window.location.search);
    name = urlParams.get('name');
    const id = urlParams.get('id');
    if(changedname != ""){
        name = changedname;
        window.location = "./myprofile.html" + "?" +  "id=" + id + "&name=" + name

    }

    $("h5").html("User Name: " + name + "</br> User ID: " + id);
    $("#change_username_input").attr("placeholder", name);

}
function GetURL(keys, values) {
    txt = "?";
    for (i = 0, len = keys.length; i < len; i++) {
        txt += keys[i] + "=" + values[i] + "&";
    }
    return txt.substring(0, txt.length - 1);
}

function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
    $("div.notification").html("<p class='error'>" + msg + "</p>");
}
function UsernameChangedSuccessfully() {
    // $("#change_username_input").value = 
    alert("changed");
    UpdateUserInfo($("#change_username_input").val())
}

$(document).ready(function () {
    UpdateUserInfo();
    $("#all_bookables_btn").click(function () {

        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        window.location = "./all-bookables.html" + GetURL(["id", "name"], [id, name]);

    });
    $("#my_bookables_btn").click(function () {

        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        window.location = "./mybookables.html" + GetURL(["id", "name"], [id, name]);

    });
    $("#change_username_btn").click(function () {
        var data = { "name": $("#change_username_input").val() };
        console.log(JSON.stringify(data));
        $.ajax({
            url: "http://localhost:5000/api/users/1/",
            type: "PUT",
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            headers: { 'Access-Control-Allow-Origin': '*' },
            success: UsernameChangedSuccessfully,
            error: renderError
        });

    });
});