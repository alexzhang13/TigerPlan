/* Script for handling Events Calendar */
var calendarList = [];

/* List of scheduleIds */
var scheduleIds = [];
var nextId = 0;

function addCalendar(calendar) {
    calendarList.push(calendar);
}

const calendarId = "1";
let cal;

function renderTimeSelectionCalendar(calendarDivId) {
    if (!calendarDivId) {
        calendarDivId = "#calendar";
    }
    cal = new tui.Calendar(calendarDivId, {
        id: calendarId,
        defaultView: 'week',
        taskView: false,
        scheduleView: ['time'],
        useCreationPopup: true,
        useDetailPopup: true,
        template: templates
    });

    // register templates
    var templates = {
        popupStateFree: function () {
            return 'Free';
        },
        popupStateBusy: function () {
            return 'Busy';
        },
        titlePlaceholder: function () {
            return 'Subject';
        },
        locationPlaceholder: function () {
            return 'Location';
        },
        startDatePlaceholder: function () {
            return 'Start date';
        },
        endDatePlaceholder: function () {
            return 'End date';
        },
        popupSave: function () {
            return 'Save';
        },
        popupUpdate: function () {
            return 'Update';
        },
        popupDetailDate: function (isAllDay, start, end) {
            var isSameDate = moment(start).isSame(end);
            var endFormat = (isSameDate ? '' : 'YYYY.MM.DD ') + 'hh:mm a';

            if (isAllDay) {
                return moment(start).format('YYYY.MM.DD') + (isSameDate ? '' : ' - ' + moment(end).format('YYYY.MM.DD'));
            }

            return (moment(start).format('YYYY.MM.DD hh:mm a') + ' - ' + moment(end).format(endFormat));
        },
        popupDetailUser: function (schedule) {
            return 'User : ' + (schedule.attendees || []).join(', ');
        },
        popupDetailState: function (schedule) {
            return 'State : ' + schedule.state || 'Busy';
        },
        popupDetailRepeat: function (schedule) {
            return 'Repeat : ' + schedule.recurrenceRule;
        },
        popupDetailBody: function (schedule) {
            return 'Body : ' + schedule.body;
        },
        popupEdit: function () {
            return 'Edit';
        },
        popupDelete: function () {
            return 'Delete';
        }

    };

    cal.on({
        'clickMore': function (e) {
            console.log('clickMore', e);
        },
        'clickSchedule': function (e) {
            console.log(e);
        },
        'clickDayname': function (date) {
            console.log('clickDayname', date);
        },
        'beforeCreateSchedule': function (e) {

            // $("#create").fadeIn();
            saveNewSchedule(e);
        },
        'beforeUpdateSchedule': function (e) {
            var schedule = e.schedule;
            var changes = e.changes;

            console.log('Update schedule with id: ' + e.schedule.id);

            // prevent changes from overwriting calendarId
            // DOES NOT WORK WITHOUT
            if (changes && changes.calendarId) {
                delete changes.calendarId;
            }

            cal.updateSchedule(schedule.id, schedule.calendarId, changes);

            // refreshScheduleVisibility();
        },
        'beforeDeleteSchedule': function (e) {
            // UPDATE ON DB ON FLASK
            deleteSchedule(e);

        },
        'afterRenderSchedule': function (e) {
            var schedule = e.schedule;
            // var element = cal.getElement(schedule.id, schedule.calendarId);
            // console.log('afterRenderSchedule', element);
        },
        'clickTimezonesCollapseBtn': function (timezonesCollapsed) {
            console.log('timezonesCollapsed', timezonesCollapsed);

            if (timezonesCollapsed) {
                cal.setTheme({
                    'week.daygridLeft.width': '77px',
                    'week.timegridLeft.width': '77px'
                });
            } else {
                cal.setTheme({
                    'week.daygridLeft.width': '60px',
                    'week.timegridLeft.width': '60px'
                });
            }

            return true;
        }

    });
}

function deleteSchedule(e) {
    console.log('beforeDeleteSchedule', e);
    const index = scheduleIds.indexOf(e.schedule.id);
    if (index > -1) {
        scheduleIds.splice(index, 1);
    }
    cal.deleteSchedule(e.schedule.id, e.schedule.calendarId);
}

function destroyTimeSelectionCalendar() {
    cal.destroy();
}

function getAllSchedules() {
    var schedules = [];
    for (let i = 0; i < scheduleIds.length; i++) {
        var schedule = cal.getSchedule(scheduleIds[i], calendarId);
        schedules.push(schedule);
    }
    return schedules;
}

function uploadToServer() {
    console.log(scheduleIds);
    if (scheduleIds[0]) {
        console.log(scheduleIds[0], calendarId);
        console.log(cal.getSchedule(scheduleIds[0], calendarId));
    }
    console.log(variable);
}

function saveNewSchedule(scheduleData) {
    console.log("Saving " + scheduleData);
    var randomColor = Math.floor(Math.random() * 16777215).toString(16);
    var strId = nextId.toString();
    nextId += 1;
    var schedule = {
        id: strId,
        calendarId: calendarId,
        title: scheduleData.title,
        start: scheduleData.start,
        end: scheduleData.end,
        color: "#111111",
        bgColor: "#93ea7f",
        dragBgColor: "#93ea7f",
        borderColor: '#FDF8F3',
        category: 'time',
        location: scheduleData.location
    };

    cal.createSchedules([schedule]);
    scheduleIds.push(strId);
}

function refreshScheduleVisibility() {
    var calendarElements = Array.prototype.slice.call(document.querySelectorAll('#calendarList input'));

    calendarList.forEach(function (calendar) {
        cal.toggleSchedules(calendar.id, !calendar.checked, false);
    });

    cal.render(true);

    calendarElements.forEach(function (input) {
        var span = input.nextElementSibling;
        span.style.backgroundColor = input.checked ? span.style.borderColor : 'transparent';
    });
}