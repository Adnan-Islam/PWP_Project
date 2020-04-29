"use strict";

function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
    $("div.notification").html("<p class='error'>" + msg + "</p>");
}
function UsernameChangedSuccessfully() {
    // $("#change_username_input").value = 
    alert("changed");
}
$(document).ready(function () {


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
