(function() {
    $('#id_body_type').change(function () {
        if ($('#id_body_type').val() == '1'){
            $('#id_body_type').hide();
            $('#id_body_type').show();
        }
    })
})();