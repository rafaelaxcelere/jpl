odoo.define('odoo_attendance_task_extended.my_attendances', function (require) {
"use strict";
    var core = require('web.core');
    var Model = require('web.Model');
    var Widget = require('web.Widget');

    var QWeb = core.qweb;
    var _t = core._t;
    var hr_attendance = require('hr_attendance.my_attendances');
    var greeting_message = require('hr_attendance.greeting_message');

    hr_attendance.include({
        // hr_attendance code to ignore odoo_attendance_task changes
        start: function () {
            var self = this;

            var hr_employee = new Model('hr.employee');
            hr_employee.query(['attendance_state', 'name'])
                .filter([['user_id', '=', self.session.uid]])
                .all()
                .then(function (res) {
                    if (_.isEmpty(res) ) {
                        self.$('.o_hr_attendance_employee').append(_t("Error : Could not find employee linked to user"));
                        return;
                    }
                    self.employee = res[0];
                    self.$el.html(QWeb.render("HrAttendanceMyMainMenu", {widget: self}));
                });

            return this._super.apply(this, arguments);
        },
        update_attendance: function () {
            var self = this;
            var hr_employee = new Model('hr.employee');
            hr_employee.call('attendance_manual', [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'])
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                    }
                });
        },
    });
});
