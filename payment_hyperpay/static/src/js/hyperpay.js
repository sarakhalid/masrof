var wpwlOptions = {
      onReady: function(){
        var shopOrigin = $('input[name="shopOrigin"]');
        var origin = parent.window.location.origin;
        parent_iframe = $('#hyperpay_iframe', window.parent.document);
        parent_iframe.css({"width":"100%", "height":"21em", "border":"none", "display":""});
        $('.hyperpay_loader', window.parent.document).remove();
        $('#hyperpay_close', window.parent.document).on('click', function(){
            parent.window.location.reload(true);
            });
        if (shopOrigin.length != 0 && shopOrigin.val() == 'null'){
            shopOrigin.val(origin);
        }
      }
    }
