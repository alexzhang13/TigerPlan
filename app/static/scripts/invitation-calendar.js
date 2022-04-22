/* Script for handling Invitation Calendar */
var calendarList = [];

/* List of scheduleIds */
var timeblockAvailabilities;

function addCalendar(calendar) {
    calendarList.push(calendar);
}

const calendarId = "1";
let cal = null;

function renderTimeSelectionCalendar(calendarDivId) {
    if (cal != null) {
        destroyInvitationCalendar();
    }

    if (!calendarDivId) {
        calendarDivId = "#calendar";
    }
    cal = new tui.Calendar(calendarDivId, {
        id: calendarId,
        defaultView: 'week',
        taskView: false,
        isReadOnly: true,
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
            if (e.schedule.raw != "EventTimeBlock") {
                return;
            }

            if (timeblockAvailabilities[e.schedule.id]) {
                cal.updateSchedule(e.schedule.id, calendarId, {
                    bgColor: eventColorUnselected,
                    color: "#999999"
                });
                timeblockAvailabilities[e.schedule.id] = false;
            } else {
                cal.updateSchedule(e.schedule.id, calendarId, {
                    bgColor: eventColorSelected,
                    color: "#000000"
                });
                timeblockAvailabilities[e.schedule.id] = true;
            }
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

const conflictColor = "#dddddd";
const eventColorSelected = "#f7349e";
const eventColorUnselected = "#ffe7ff";

function renderUserConflicts(response) {
    var userConflictsList = [];
    for (let i = 0; i < response.length; i++) {

        var d = {
            id: response[i].id,
            calendarId: '1',
            title: response[i].name,
            category: 'time',
            dueDateClass: '',
            start: response[i].start + 'Z',
            end: response[i].end + 'Z',
            bgColor: conflictColor,
            dragBgColor: conflictColor,
            raw: "UserConflict"
        }
        userConflictsList.push(d);
    }
    console.log(userConflictsList);
    cal.createSchedules(userConflictsList);
}

function renderEventTimeBlocks(eventTimes) {
    var eventTimesList = [];
    timeblockAvailabilities = {};
    console.log(eventTimes);
    for (let i = 0; i < eventTimes.length; i++) {

        var d = {
            id: eventTimes[i].id,
            calendarId: '1',
            title: eventTimes[i].name,
            category: 'time',
            dueDateClass: '',
            start: eventTimes[i].start + 'Z',
            end: eventTimes[i].end + 'Z',
            bgColor: eventColorUnselected,
            color: "#999999",
            raw: "EventTimeBlock"
        }
        eventTimesList.push(d);
        timeblockAvailabilities[eventTimes[i].id] = false;
    }
    console.log(eventTimesList);
    cal.createSchedules(eventTimesList);
}

function errorWhileFetchingTimeBlocks(error) {
    console.log(error);
}

function destroyInvitationCalendar() {
    cal.destroy();
    cal = null;
}

function getAllSelections() {
    return timeblockAvailabilities;
}


