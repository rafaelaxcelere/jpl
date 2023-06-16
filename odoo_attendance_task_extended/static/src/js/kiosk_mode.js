odoo.define('odoo_attendance_task_extended.kiosk_mode', function (require) {
    "use strict";

    var KioskMode= require('hr_attendance.kiosk_mode');

    KioskMode.include({
        start: function () {
        console.log('start_mode');
        window.location.hash="no-back-button";
        window.location.hash="Again-No-back-button";//again because google chrome don't insert first hash into history
        window.onhashchange=function(){window.location.hash="no-back-button";}
        var self = this;
        return self._super.apply(this, arguments);
    },
    })
})
