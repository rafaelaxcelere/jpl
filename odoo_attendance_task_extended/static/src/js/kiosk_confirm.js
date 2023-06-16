odoo.define('odoo_attendance_task_extended.kiosk_confirm', function (require) {
    "use strict";
    var core = require('web.core');
    var Model = require('web.Model');
    var Widget = require('web.Widget');
    var data_manager = require('web.data_manager');
    var ViewManager = require('web.ViewManager');
    var QWeb = core.qweb;
    var _t = core._t;
    var KioskConfirm = require('hr_attendance.kiosk_confirm');

    document.onmouseover = function() {
        //User's mouse is inside the page.
        window.innerDocClick = true;
    },

    document.onmouseleave = function() {
        //User's mouse has left the page.
        window.innerDocClick = false;
    },


    window.onhashchange = function() {
        if (window.innerDocClick) {
            window.innerDocClick = false;
            console.log("1");
        } else {
            if (window.location.hash != '#undefined') {
                console.log("2");
            } else {
                console.log("3");
                history.pushState("", document.title, window.location.pathname);
                location.reload();
            }
        }
    },


    ViewManager.include({
        do_load_state: function(state, warm) {
            if (state.view_type && state.view_type !== this.active_view.type) {
                this.switch_mode(state.view_type, true);
            }
            if (this.active_view) {
                this.active_view.controller.do_load_state(state, warm);
            }
        },
    });

    KioskConfirm.include({
        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.task =  action.task;
            this.task_id = action.task_id;
        },
        start: function () {
            window.location.hash="no-back-button";
            window.location.hash="Again-No-back-button";//again because google chrome don't insert first hash into history
            window.onhashchange=function(){window.location.hash="no-back-button";}
            var self = this;
            this.clicked = false;
            self.session.user_has_group('hr_attendance.group_hr_attendance_use_pin').then(function (has_group) {
                self.use_pin = has_group;


                var hr_employee = new Model('hr.employee');

                hr_employee.call('get_employee_task', [[self.employee_id]], {}, {async: false}).then(function (res) {
                    if (self.task == undefined && self.employee_state == 'checked_in'){
                        self.task = res.name;
                        self.task_id = res.id;
                    }
                    self.out_task = res.name;
                    });

                self.$el.html(QWeb.render("HrAttendanceKioskConfirm", {widget: self}));
            });

            return self._super.apply(this, arguments);
        },
        events: {
            "click .o_hr_attendance_button_tasks": function(){
                this.do_action('odoo_attendance_task_extended.hr_attendance_task_action_kanban', {additional_context:{'employee_id':this.employee_id}});
                window.location.hash="no-back-button";
                window.location.hash="Again-No-back-button";//again because google chrome don't insert first hash into history
                window.onhashchange=function(){window.location.hash="no-back-button";}
                },

            "click .o_hr_attendance_back_button": function () {
                this.do_action(this.next_action, {clear_breadcrumbs: true});
            },
            "click .o_hr_attendance_sign_in_out_icon": function () {
                this.$('.o_hr_attendance_sign_in_out_icon').attr("disabled", "disabled");
            }
            ,
            'click .o_hr_attendance_pin_pad_button_0': function () {
                this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 0);
                this.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled");
            }

            ,
            'click .o_hr_attendance_pin_pad_button_1': function () {
                this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 1);
                this.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled");
            }

            ,
            'click .o_hr_attendance_pin_pad_button_2': function () {
                this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 2);
                this.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled");
            }

            ,
            'click .o_hr_attendance_pin_pad_button_3': function () {
                this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 3);
                this.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled");
            }

            ,
            'click .o_hr_attendance_pin_pad_button_4': function () {
                this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 4);
                this.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled");
            }

            ,
            'click .o_hr_attendance_pin_pad_button_5': function () {
                this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 5);
                this.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled");
            }

            ,
            'click .o_hr_attendance_pin_pad_button_6': function () {
                this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 6);
                this.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled");
            }

            ,
            'click .o_hr_attendance_pin_pad_button_7': function () {
                this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 7);
                this.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled");
            }

            ,
            'click .o_hr_attendance_pin_pad_button_8': function () {
                this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 8);
                this.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled");
            }

            ,
            'click .o_hr_attendance_pin_pad_button_9': function () {
                this.$('.o_hr_attendance_PINbox').val(this.$('.o_hr_attendance_PINbox').val() + 9);
                this.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled");
            }

            ,
            'click .o_hr_attendance_pin_pad_button_C': function () {
                this.$('.o_hr_attendance_PINbox').val('');
            }

            ,
            'click .o_hr_attendance_pin_pad_button_ok': function () {
                if (this.clicked){
                    this.$('.o_hr_attendance_pin_pad_button_ok').attr("disabled", "disabled")
                    console.log('Ya clickeado.');
                }
                else {
                    this.clicked = true;
                    var self = this;
                    this.$('.o_hr_attendance_pin_pad_button_ok').attr("disabled", "disabled");
                    var hr_employee = new Model('hr.employee');
                    var hr_attendance_model = new Model('hr.attendance');
                    var pin = this.$('.o_hr_attendance_PINbox').val();
                    if (pin.length > 0) {
                        hr_employee.call('attendance_manual', [[this.employee_id], this.next_action, pin, self.task_id, self.task])
                            .then(function (result) {
                                if (result.action) {
                                    var id = result.action.attendance['id'];
                                    hr_attendance_model.call('add_employee_task', [[id], self.task_id, self.task], {}, {async: false});
                                    self.do_action(result.action);
                                } else if (result.warning) {
                                    self.clicked = false;
                                    self.do_warn(result.warning);
                                    setTimeout(function () {
                                        self.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled");
                                    }, 500);
                                }
                            });
                    }
                    else {
                        // if (self.task.length == 0)
                        //     $('#task').css('border', '1px solid red');
                        if (pin.length == 0)
                            $('.o_hr_attendance_PINbox').css('border', '1px solid red');
                    }
                }
            }

        },

    })

});
