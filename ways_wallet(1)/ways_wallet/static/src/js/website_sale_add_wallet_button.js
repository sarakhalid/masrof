//Copyright 2020 Shurshilov Artem <shurshilov.a@yandex.ru>
odoo.define("website_sale_add_wallet", function(require) {
    "use strict";
    var ajax = require("web.ajax");

            $(document).ready(function(){

                    $(this).on("click", " #add_wallet_button", function() {
                        ajax.jsonRpc("/add_wallet", "call", {}).then(function() {
                            
                        });
                        return window.location = '/shop/payment';
                });
            });
});
