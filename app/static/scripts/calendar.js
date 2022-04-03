/* Script for handling Events Calendar */
var calendarList = [];

function addCalendar(calendar) {
    calendarList.push(calendar);
}

var cal = new tui.Calendar('#calendar', {
    id: "1",
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

        console.log('beforeUpdateSchedule', e);

        cal.updateSchedule(schedule.id, schedule.calendarId, changes);
        // UPDATE ON DB ON FLASK

        refreshScheduleVisibility();
    },
    'beforeDeleteSchedule': function (e) {
        console.log('beforeDeleteSchedule', e);
        cal.deleteSchedule(e.schedule.id, e.schedule.calendarId);
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

function saveNewSchedule(scheduleData) {
    console.log('scheduleData ', scheduleData)
    var randomColor = Math.floor(Math.random() * 16777215).toString(16);
    var schedule = {
        id: '1',
        title: scheduleData.title,
        start: scheduleData.start,
        end: scheduleData.end,
        color: "#111111",
        bgColor: "#" + randomColor,
        dragBgColor: "#" + randomColor,
        borderColor: '#FDF8F3',
        category: 'time',
        // category: scheduleData.isAllDay ? 'allday' : 'time',
        // dueDateClass: '',
        location: scheduleData.location,
        // raw: {
        //     class: scheduleData.raw['class']
        // },
        // state: scheduleData.state
    };

    cal.createSchedules([schedule]);

    // refreshScheduleVisibility();
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

$(document).ready(function() {
    calendarList.push(cal);
    cal.createSchedules([
        {
            id: '1',
            calendarId: '1',
            title: 'my schedule',
            category: 'time',
            dueDateClass: '',
            start: '2022-04-3T2:30:00+09:00',
            end: '2022-04-3T03:30:00+09:00'
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
});
