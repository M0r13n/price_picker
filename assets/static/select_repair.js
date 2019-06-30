$(document).ready(function () {
    /*Toggle selected cards*/
    $('.selectable').click(function () {
        $(this).toggleClass('border-primary');
    });

    /*Catch form submission and fill selected choices*/
    $('#repairSubmitBtn').click(function (e) {
        e.preventDefault();
        let selected_repair_ids = $('.card.border-primary').map(function () {
            return $(this).data('id');
        }).get();
        $('#repairs').val(selected_repair_ids);
        $('#repairSubmitForm').submit();
    });

});