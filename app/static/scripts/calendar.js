/* Script for handling Events Calendar */
var Calendar = tui.Calendar;

var cal = new tui.Calendar('#calendar', {
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

cal.createSchedules([
    {
        id: '1',
        calendarId: '1',
        title: 'my schedule',
        category: 'time',
        dueDateClass: '',
        start: '2022-04-1T22:30:00+09:00',
        end: '2022-04-1T02:30:00+09:00'
    },
    {
        id: '2',
        calendarId: '1',
        title: 'second schedule',
        category: 'time',
        dueDateClass: '',
        start: '2018-01-18T17:30:00+09:00',
        end: '2018-01-19T17:31:00+09:00',
        isReadOnly: true    // schedule is read-only
    }
]);