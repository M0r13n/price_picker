$(document).ready(function () {
    $('#mailTestBtn').click(function () {
        $.ajax({
            url: '/admin/mail/test',
            type: 'GET'
        })
    });
});