$(document).ready(function () {
    /*Toggle selected cards*/
    $('.selectable').click(function () {
        $('.selectable').toggleClass('border-primary', false);
        $(this).toggleClass('border-primary');
    });

    /*Catch form submission and fill selected choices*/
    $('#colorFormSubmitBtn').click(function (e) {
        e.preventDefault();
        let selected_color_ids = $('.card.border-primary').map(function () {
            return $(this).data('id');
        }).get();
        $('#colors').val(selected_color_ids);
        $('#colorForm').submit();
    });

});