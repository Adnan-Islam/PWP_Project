function GetURL(keys, values) {
    txt = "?";
    for (i = 0, len = keys.length; i < len; i++) {
        txt += keys[i] + "=" + values[i] + "&";
    }
    return txt.substring(0, txt.length - 1);
}

function GetMySlot() {
    const urlParams = new URLSearchParams(window.location.search);
    const name = urlParams.get('name');
    const id = urlParams.get('id');
    const bookable_id = urlParams.get('bookable_id');
    const slot_id = urlParams.get('slot_id');

    $.ajax({
        url: "http://localhost:5000/api/users/" + id + "/" + "my_bookables/" + bookable_id + "/slots/" + slot_id + "/",
        type: "GET",
        headers: { 'Access-Control-Allow-Origin': '*' },
        success: function (body, status, jqxhr) {
            console.log(body);
            slot_body = body;
            $.ajax({
                url: "http://localhost:5000/api/users/" + id + "/" + "my_bookables/" + bookable_id + "/",
                headers: { 'Access-Control-Allow-Origin': '*' },
                success: function (body, status, jqxhr) {
                    RenderItems(slot_body, body);
                },
                error: function (jqxhr, type, error) {
                    console.log("ERROR (" + type + ") - " + error);
                }
            });

        },
        error: function (jqxhr, type, error) {
            console.log("ERROR (" + type + ") - " + error);
        }
    });
}
function RenderItems(slot, bookable) {
    const urlParams = new URLSearchParams(window.location.search);
    const name = urlParams.get('name');
    const id = urlParams.get('id');
    const bookable_id = urlParams.get('bookable_id');
    const slot_id = urlParams.get('slot_id');
    $("h5").html("Slot Information </br> Slot ID: " + slot_id + "</br> Client ID: " + id + "</br> Availibility: " + slot.availability);
    html = "<tr><th> Starts </th><th> Ends </th><th> Description </th></tr>";
    html += "<tr>"
        + "<td>" + slot.starting_time + "</td>"
        + "<td>" + slot.ending_time + "</td>"
        + "<td>" + bookable.details
        + "</td>"
        + "</tr>";
    $("#slot_table").html(html);
}
$(document).ready(function () {
    GetMySlot();

    $("#back_to_slots").click(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        const bookable_id = urlParams.get('bookable_id');
        const slot_id = urlParams.get('slot_id');

        window.location = "./my_slots.html" + GetURL(["id", "name", "bookable_id"], [id, name, bookable_id]);

    });
    $("#edit_btn").click(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        const bookable_id = urlParams.get('bookable_id');
        const slot_id = urlParams.get('slot_id');

        window.location = "./edit_slot.html" + GetURL(["id", "name", "bookable_id", "slot_id"], [id, name, bookable_id, slot_id]);

    });
    $("#delete_btn").click(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        const bookable_id = urlParams.get('bookable_id');
        const slot_id = urlParams.get('slot_id');

        $.ajax({
            url: "http://localhost:5000/api/users/" + id + "/" + "my_bookables/" + bookable_id + "/slots/" + slot_id + "/",
            type: "DELETE",
            headers: { 'Access-Control-Allow-Origin': '*' },
            success: function (body, status, jqxhr) {
                window.location = "./my_slots.html" + GetURL(["id", "name", "bookable_id"], [id, name, bookable_id]);
            },
            error: function (jqxhr, type, error) {
                console.log("ERROR (" + type + ") - " + error);
            }
        });
    });
});