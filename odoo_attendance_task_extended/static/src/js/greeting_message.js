odoo.define('odoo_attendance_task_extended.greeting_message', function (require) {
    "use strict";

    var greeting_message = require('hr_attendance.greeting_message');

    var core = require('web.core');
    var Model = require('web.Model');

    var greeting_message = require('hr_attendance.greeting_message');

    greeting_message.include({
        init: function (parent, action) {
            var self = this;
            var hr_employee = new Model('hr.employee');
            var employee_id = action.attendance.employee_id[0];

            hr_employee.call('get_old_and_new_task', [[employee_id]], {}, {async: false}).then(function (res) {
                self.out_task = res.out_task;
                self.in_task = res.in_task;
                self.in_attendance = res.in_attendance;
                if (res.out_attendance.hours_today) {
                    var duration = moment.duration(res.out_attendance.hours_today, "hours");
                    self.hours_today = duration.hours() + ' h, ' + duration.minutes() + ' m';
                }
                self.out_attendance = res.out_attendance;
                self.in_attendance.check_in_time = (new Date((new Date(self.in_attendance.check_in)).valueOf() - (new Date()).getTimezoneOffset() * 60 * 1000)).toTimeString().slice(0, 8);
                self.in_attendance.check_out_time = self.in_attendance.check_out && (new Date((new Date(self.in_attendance.check_out)).valueOf() - (new Date()).getTimezoneOffset() * 60 * 1000)).toTimeString().slice(0, 8);
                self.out_attendance.check_in_time = (new Date((new Date(self.out_attendance.check_in)).valueOf() - (new Date()).getTimezoneOffset() * 60 * 1000)).toTimeString().slice(0, 8);
                self.out_attendance.check_out_time = self.out_attendance.check_out && (new Date((new Date(self.out_attendance.check_out)).valueOf() - (new Date()).getTimezoneOffset() * 60 * 1000)).toTimeString().slice(0, 8);
            });

            self._super(parent, action);
        },
    });

});
