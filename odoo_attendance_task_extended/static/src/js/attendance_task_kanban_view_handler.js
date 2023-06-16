
odoo.define('odoo_attendance_task_extended.attendance_task_kanban_view_handler', function(require) {
"use strict";

var KanbanRecord = require('web_kanban.Record');

KanbanRecord.include({
    on_card_clicked: function() {
        if (this.model === 'hr.attendance.task' && this.$el.parents('.o_attendance_task_kanban').length) {
                                            // needed to differentiate : check in/out kanban view of attendance tasks <-> standard attendance task kanban view
            var action = {
                type: 'ir.actions.client',
                name: 'Confirm',
                tag: 'hr_attendance_kiosk_confirm',
                employee_id: this.record.active_employee_id.raw_value[0],
                employee_name: this.record.active_employee_id.raw_value[1],
                employee_state: this.record.active_employee_id_attendance_state.raw_value,
                task: this.record.name.raw_value,
                task_id: this.record.id.raw_value,
            };
            this.do_action(action);
        } else {
            this._super.apply(this, arguments);
        }
    }
});

});
