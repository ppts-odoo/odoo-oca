/** @odoo-module **/
odoo.define('mask.widget', function (require) {
"use strict";
var AbstractField = require('web.AbstractField');
var fieldRegistry = require('web.field_registry');
var MaskWidget = AbstractField.extend({
template:"FieldMaskDigits",
start: function(){
    this._super.apply(this, arguments);
    if(this.recordData[this.nodeOptions.current_value]);
    },
_render: function(){
    var val = this.value;
    var show_value;

    if (val){
        show_value =[...val].reduce((acc, x, i) => (i < val.length - 4) ? acc+'*' : acc+x , '');
        this.$el.text(show_value);
    }
    else {
    show_value = "";
    }

    this.$('mask_digits').text(show_value.toString());

    }
});

fieldRegistry.add('mask_digits', MaskWidget);
});

