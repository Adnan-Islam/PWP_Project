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
        const bookable_id = urlParams.get('bookable_id');
        if($("#availability_radio").is(':checked')){
        var data = { "starting_time": $("#starting_time_input").val(), "ending_time": $("#ending_time_input").val(), "availability": true };
        }
        else{
            var data = { "starting_time": $("#starting_time_input").val(), "ending_time": $("#ending_time_input").val(), "availability": false };
        }

        $.ajax({
            url: "http://localhost:5000/api/users/" + id + "/my_bookables/" + bookable_id +"/slots/",
            type: "POST",
            data: JSON.stringify(data),
            contentType: "application/vnd.mason+json; charset=utf-8",
            headers: { 'Access-Control-Allow-Origin': '*' },
            success: function (status, jqxhr) {
                window.location = "../html/my_slots.html" + GetURL(["id", "name", "bookable_id"], [id, name, bookable_id]);

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
        const bookable_id = urlParams.get('bookable_id');
        window.location = "../html/my_slots.html" + GetURL(["id", "name", "bookable_id"], [id, name, bookable_id]);
    });
});