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

        var data = {
            id: schedule.id,
            title: schedule.title,
            start: e.changes.start.toUTCString(),
            end: e.changes.end.toUTCString(),
        }
        
        var url = '/update_conflict'

        console.log(data)
        $.ajax({
            type: "POST",
            url: url,
            data: JSON.stringify(data),
            dataType: "json",
            success: function (response) {
                console.log(response)
            },
            error: function (error) {
                console.log(error);
            }
        });

        // UPDATE ON DB ON FLASK

        refreshScheduleVisibility();
    },
    'beforeDeleteSchedule': function (e) {
        console.log('beforeDeleteSchedule', e);
        cal.deleteSchedule(e.schedule.id, e.schedule.calendarId);
        // UPDATE ON DB ON FLASK

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

function getHashId (startTime, endTime) {
    var first = startTime.toString(36);
    var second = endTime.toString(36);
    return first + second;
}

function deleteSchedule(scheduleData) {
    
}

function saveNewSchedule(scheduleData) {
    console.log('scheduleData ', scheduleData)
    var randomColor = Math.floor(Math.random() * 16777215).toString(16);
    var randomId = Math.floor(Math.random() * 22345679).toString(16);

    // figure out better ID genereation
    var hashId = getHashId(scheduleData.start, scheduleData.end);
    var schedule = {
        id: randomId,
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

    // call ajax to save calendar
    let url = '/saveNewSchedule'
    console.log(JSON.stringify( schedule ))

    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify( schedule ),
        dataType: "json",
        success: function (response) {
            console.log(response)
        },
        error: function (error) {
            console.log(error);
        }
    });

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

$(document).ready(function () {
    addCalendar(cal);

    // call ajax to load calendar
    let url = '/load_conflicts'

    var toCreate = []
    schedules = $.ajax({
        type: "GET",
        url: url,
        success: function (response) {
            console.log(response)
            for (let i = 0; i < response.length; i++) {
                var randomColor = Math.floor(Math.random() * 16777215).toString(16);
                var d = {
                    id: response[i].id,
                    calendarId: '1',
                    title: response[i].name,
                    category: 'time',
                    dueDateClass: '',
                    start: response[i].start + 'Z',
                    end: response[i].end + 'Z',
                    bgColor: "#808080",
                    dragBgColor: "#808080",
                    isReadOnly: true
                }
                toCreate.push(d);
                console.log(toCreate)
            }
            cal.createSchedules(toCreate);
        },
        error: function (error) {
            console.log(error);
        }
    });
});