function addCart() {
    $.post("/dukkan/sepet/ekle/", { product_id: $('#product_id').val(), quantity: $('#quantity').val(), csrfmiddlewaretoken: $('#csrfmiddlewaretoken').val() },
            function(data){
                if (data=='OK') {
                    $.get('/dukkan/sepet/', function(data) { $('#cart').html(data); } );
                }
            });
}
