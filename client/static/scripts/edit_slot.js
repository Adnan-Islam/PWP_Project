function GetURL(keys, values) {
    txt = "?";
    for (i = 0, len = keys.length; i < len; i++) {
        txt += keys[i] + "=" + values[i] + "&";
    }
    return txt.substring(0, txt.length - 1);
}
function UpdateSlotInfo() {
    const urlParams = new URLSearchParams(window.location.search);
    const name = urlParams.get('name');
    const id = urlParams.get('id');
    const bookable_id = urlParams.get('bookable_id');
    const slot_id = urlParams.get('slot_id');

    $.ajax({
        url: "http://localhost:5000/api/users/" + id + "/" + "my_bookables/" + bookable_id + "/" + "slots/" + slot_id + "/",
        headers: { 'Access-Control-Allow-Origin': '*' },
        success: function (body, status, jqxhr) {
            $("#starting_time_input").attr("placeholder", "Starting Time and Data: " + body.starting_time);
            $("#ending_time_input").attr("placeholder", "Ending Time and Date: " + body.ending_time);
            if(body.availability === "true")
                $("#availability_radio").prop("checked", true);
            else
                $("#availability_radio").prop("checked", false);


        },
        error: function (jqxhr, type, error) {
            console.log("ERROR (" + type + ") - " + error);
        }
    });
}

$(document).ready(function () {
    UpdateSlotInfo();
    $("#cancel_btn").click(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        const bookable_id = urlParams.get('bookable_id');
        const slot_id = urlParams.get('slot_id');

        window.location = "./my_slot_detail.html" + GetURL(["id", "name", "bookable_id", "slot_id"], [id, name, bookable_id, slot_id]);

    });
    $("#save_btn").click(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        const bookable_id = urlParams.get('bookable_id');
        const slot_id = urlParams.get('slot_id');
        if ($("#availability_radio").is(':checked')) {
            var data = { "starting_time": $("#starting_time_input").val(), "ending_time": $("#ending_time_input").val(), "availability": true };
        }
        else {
            var data = { "starting_time": $("#starting_time_input").val(), "ending_time": $("#ending_time_input").val(), "availability": false };
        }
        $.ajax({
            url: "http://localhost:5000/api/users/" + id + "/" + "my_bookables/" + bookable_id + "/slots/" + slot_id + "/",
            type: "PUT",
            data: JSON.stringify(data),
            contentType: "application/json; charset=utf-8",
            headers: { 'Access-Control-Allow-Origin': '*' },
            success: function (body, status, jqxhr) {
                window.location = "./my_slot_detail.html" + GetURL(["id", "name", "bookable_id", "slot_id"], [id, name, bookable_id, slot_id]);
            },
            error: function (jqxhr, type, error) {
                console.log("ERROR (" + type + ") - " + error);
            }
        });
    });
});