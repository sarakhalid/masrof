odoo.define('payment_hyperpay.payment_hyperpay', function (require) {
      "use strict";

      var core = require('web.core');
      var Dialog = require('web.Dialog');
      var publicWidget = require('web.public.widget');
      var ajax = require('web.ajax');

      var qweb = core.qweb;
      var _t = core._t;

      if ($.blockUI) {
        $.blockUI.defaults.css.border = '0';
        $.blockUI.defaults.css["background-color"] = '';
        $.blockUI.defaults.overlayCSS["opacity"] = '0.5';
        $.blockUI.defaults.overlayCSS["z-index"] = '1050';
    }

    // Reference
    // https://dev.to/pulljosh/how-to-load-html-css-and-js-code-into-an-iframe-2blc
    const getGeneratedPageURL = ({ html, css, js}) => {
      const getBlobURL = (code, type) => {
        const blob = new Blob([code], { type })
        return URL.createObjectURL(blob)
      }

      const source = `
        <html>
          <head>
            ${css}
            ${js}
          </head>
          <body>
          <script>
          var wpwlOptions = {
                onReady: function(){
                  var shopOrigin = $('input[name="shopOrigin"]');
                  var origin = parent.window.location.origin;
                  parent_iframe = $('#hyperpay_iframe', window.parent.document);
                  console.log("----parent_iframe--",parent_iframe);
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
              $(document).ready(function(){
                setTimeout(function(){
                  var parent_frame = window.parent.$("#hyperpay_iframe")
                  if(parent_frame.css('display') == 'none'){
                    $('.hyperpay_loader', window.parent.document).remove();
                    parent_frame.css({"display":"block","width":"100%", "height":"21em", "border":"none"});
                    $('#hyperpay_close', window.parent.document).on('click', function(){
                      parent.window.location.reload();
                    });
                  }
                }, 3000);
              });
              </script>
            ${html || ''}
          </body>
        </html>
      `

        return getBlobURL(source, 'text/html')
      }

      var HyperpayPaymentForm = publicWidget.Widget.extend({
      init: function() {
            this.tx_id = $('#hyperpay_tx').val();
            this._initBlockUI(_t("Loading..."));
            this.start();
        },
      start: function() {
            var self = this;
            self._createHyperpayCheckoutId();
        },
      _createHyperpayCheckoutId: function() {
            var self = this;
            ajax.jsonRpc('/payment/hyperpay/checkout/create', 'call', {
                'txId': self.tx_id
            })
            .then(function (result) {
                if (result) {
                    self._renderHyperpayModal(result.checkoutId, result.domain, result.base_url,result.data_brands,result.acq);
                } else {
                      console.log('Error Occured');
                }
            });
        },
      _renderHyperpayModal: function(checkoutId, domain, base_url,data_brands,acq) {
           var self = this;
           return ajax.loadXML('/payment_hyperpay/static/src/xml/hyperpay.xml', qweb).then(function() {
                 var $modal_html = $(qweb.render('payment_hyperpay.modal'));
                 $modal_html.appendTo($('body')).modal({keyboard: false, backdrop: 'static'});
                 var style_css = '<link rel="stylesheet" href="'+base_url+'/payment_hyperpay/static/src/css/hyperpay_style.css" />'
                 var script = '<script async src="'+domain+'/v1/paymentWidgets.js?checkoutId='+checkoutId+'"></script>'
                 var js_script = '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>'
                 var shopperResultUrlTag = '<form action="'+base_url+'/payment/hyperpay/result?acq='+acq+'" class="paymentWidgets" data-brands="'+data_brands+'"></form>'
		 console.log(shopperResultUrlTag);
                 var theIframe = document.createElement("iframe");
                 theIframe.id = "hyperpay_iframe";
                 theIframe.style = "display:none";
                 var html = script + shopperResultUrlTag;

                 const url = getGeneratedPageURL({
                  html: html,
                  css: style_css,
                  js: js_script
                    })
                 theIframe.src = url;
                 $('#hyperpay-modal-body')[0].appendChild(theIframe);

           }).catch(function (err) {
                    console.log('component error:', err);
            });

        },
        _initBlockUI: function(message) {
            if ($.blockUI) {
                $.blockUI({
                    'message': '<h2 class="text-white"><img src="/web/static/src/img/spin.png" class="fa-pulse"/>' +
                            '    <br />' + message +
                            '</h2>'
                });
            }
            $("#o_payment_form_pay").attr('disabled', 'disabled');
        },

      });

      new HyperpayPaymentForm();

});
