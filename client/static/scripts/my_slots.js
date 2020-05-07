function GetURL(keys, values) {
    txt = "?";
    for (i = 0, len = keys.length; i < len; i++) {
        txt += keys[i] + "=" + values[i] + "&";
    }
    return txt.substring(0, txt.length - 1);
}

function GetMySlots() {
    const urlParams = new URLSearchParams(window.location.search);
    const name = urlParams.get('name');
    const id = urlParams.get('id');
    const bookable_id = urlParams.get('bookable_id');
    $.ajax({
        url: "http://localhost:5000/api/users/" + id + "/" + "my_bookables/" + bookable_id + "/slots/",
        type: "GET",
        headers: { 'Access-Control-Allow-Origin': '*' },
        success: function (body, status, jqxhr) {
            console.log(body);
            RenderItems(body.items);

        },
        error: function (jqxhr, type, error) {
            console.log("ERROR (" + type + ") - " + error);
        }
    });
}
function RenderItems(items) {
    const urlParams = new URLSearchParams(window.location.search);
    const name = urlParams.get('name');
    const id = urlParams.get('id');
    const bookable_id = urlParams.get('bookable_id');
    console.log(items[0].starting_time);
    html = "<tr><th> Starts </th><th> Ends </th><th> Availibility </th></tr>";
    for (let i = 0; i < items.length; i++) {
        html += "<tr>"
            + "<td>" + items[i].starting_time + "</td>"
            + "<td>" + items[i].ending_time  + "</td>"
            + "<td>" + items[i].availability  + "<a href=../html/my_slot_detail.html" + GetURL(["id", "name", "bookable_id", "slot_id"], [id, name, bookable_id, items[i].id]) + " target=_parent>"
            + "<button class=table_button id=table_button" + items[i].id + "> details</button></a>"
            + "</td>"
            + "</tr>";
    }
    $("#slot_table").html(html);
}
$(document).ready(function () {
    GetMySlots();

    $("#go_back_btn").click(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        const bookable_id = urlParams.get('bookable_id');

        window.location = "./my_bookable_detail.html" + GetURL(["id", "name", "bookable_id"], [id, name, bookable_id]);

    });
    $("#new_slot_btn").click(function () {
        const urlParams = new URLSearchParams(window.location.search);
        const name = urlParams.get('name');
        const id = urlParams.get('id');
        const bookable_id = urlParams.get('bookable_id');

        window.location = "./new_slot.html" + GetURL(["id", "name", "bookable_id"], [id, name, bookable_id]);

    });
});