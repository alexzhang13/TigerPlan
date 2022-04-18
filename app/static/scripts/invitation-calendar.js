/* Script for handling Events Calendar */
var calendarList = [];

/* List of scheduleIds */
var timeblockIds = [];
var timeblockAvailabilities;
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
        // isReadOnly: true,
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
            cal.updateSchedule(e.schedule.id, calendarId, {
                bgColor: "#93ea7f"
            });
        },
        'clickDayname': function (date) {
            console.log('clickDayname', date);
        },
        'beforeCreateSchedule': function (e) {
            console.log('This should not be possible. Calendar is readonly.');
            console.log('beforeCreateSchedule', e);
        },
        'beforeUpdateSchedule': function (e) {
            console.log('beforeUpdateSchedule', e);
        },
        'beforeDeleteSchedule': function (e) {
            console.log('beforeDeleteSchedule', e);
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
    const index = timeblockIds.indexOf(e.schedule.id);
    if (index > -1) {
        timeblockIds.splice(index, 1);
    }
    cal.deleteSchedule(e.schedule.id, e.schedule.calendarId);
}

function destroyInvitationCalendar() {
    cal.destroy();
}

function getAllSelections() {
    var schedules = [];
    for (let i = 0; i < timeblockIds.length; i++) {
        var schedule = cal.getSchedule(timeblockIds[i], calendarId);
        schedules.push(schedule);
    }
    return schedules;
}

function uploadToServer() {
    console.log(timeblockIds);
    if (timeblockIds[0]) {
        console.log(timeblockIds[0], calendarId);
        console.log(cal.getSchedule(timeblockIds[0], calendarId));
    }
    console.log(variable);
}

