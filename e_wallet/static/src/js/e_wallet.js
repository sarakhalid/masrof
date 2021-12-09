odoo.define('e_wallet.e_wallet', function (require) {
"use strict";

	var config = require('web.config');
	var KanbanController = require('web.KanbanController');
	var KanbanView = require('web.KanbanView');
	var ListController = require('web.ListController');
	var ListView = require('web.ListView');




var ImportControllerMixin = {
    /**
     * @override
     */
    init: function (parent, model, renderer, params) {
        this.importEnabled = params.importEnabled;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Adds an event listener on the import button.
     *
     * @private
     */
    _bindImport: function () {
        if (!this.$buttons) {
            return;
        }
        var self = this;
        this.$buttons.on('click', '.oe_action_button', function () {



var self =this
            var user = session.uid;
            rpc.query({
                model: 'res.users',
                method: 'add_wallet',
                args: [[user],{'id':user}],
                });



            
        });
    }
};



               
});


