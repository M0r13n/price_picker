$(document).ready(function () {
    /*Toggle selected cards*/
    $('.selectable').click(function () {
        $(this).toggleClass('border-primary');
        let selected_repair_ids = $('.card.border-primary').map(function () {
            return $(this).data('id');
        }).get();
        $('#repairs').val(selected_repair_ids);
    });
});