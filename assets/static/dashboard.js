$(".confirmBtn").click(function () {
    $.post("/admin/enquiry/" + $(this).prop('id') + "/complete", function (data, status) {
        location.reload();
    })
});