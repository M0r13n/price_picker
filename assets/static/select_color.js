$(document).ready(function () {
    $('.selectable').click(function () {
        $('#colors').val($(this).data('id'));
        $('#colorForm').submit();
    });

});


/*
    $('.selectable').click(function () {
        $('.selectable').toggleClass('border-primary', false);
        $(this).toggleClass('border-primary');
    });

    $('#colorFormSubmitBtn').click(function (e) {
        e.preventDefault();
        let selected_color_ids = $('.card.border-primary').map(function () {
            return $(this).data('id');
        }).get();
        $('#colors').val(selected_color_ids);
        $('#colorForm').submit();
    });
 */