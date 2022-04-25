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
    //template: templates
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
                console.log(response);
                cal.updateSchedule(schedule.id, schedule.calendarId, changes);
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

        if (!e.schedule.id) return;

        var url = '/del_conflict/' + e.schedule.id;
        $.ajax({
            type: "POST",
            url: url,
            dataType: "json",
            success: function (response) {
                console.log(response);

                cal.deleteSchedule(e.schedule.id, e.schedule.calendarId);
            },
            error: function (error) {
                console.log(error);
            }
        });

    },
    'afterRenderSchedule': function (e) {
        // var schedule = e.schedule;
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

function deleteSchedule(scheduleData) {

}

function saveNewSchedule(scheduleData) {
    var randomColor = Math.floor(Math.random() * 16777215).toString(16);
    var randomId = Math.floor(Math.random() * 22345679).toString(16);

    // figure out better ID genereation
    var schedule = {
        id: randomId,
        title: scheduleData.title,
        start: scheduleData.start,
        end: scheduleData.end,
        bgColor: "#9bd912",
        dragBgColor: "#9bd912",
        category: 'time',
        // category: scheduleData.isAllDay ? 'allday' : 'time',
        // dueDateClass: '',
        location: scheduleData.location,
        // raw: {
        //     class: scheduleData.raw['class']
        // },
        // state: scheduleData.state
    };

    // call ajax to save calendar
    let url = '/saveNewSchedule'

    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(schedule),
        dataType: "json",
        success: function (response) {
            console.log(response)
            schedule['id'] = response.id
            console.log(schedule)
            cal.createSchedules([schedule]);
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
    // call ajax to load calendar
    let url = '/load_conflicts'
    addCalendar(cal);

    var toCreate = []
    schedules = $.ajax({
        type: "GET",
        url: url,
        success: function (response) {
            console.log(response)
            for (let i = 0; i < response.length; i++) {
                console.log((new Date(response[i].start + 'Z')).toUTCString());
                var d = {
                    id: response[i].id,
                    calendarId: '1',
                    title: response[i].name,
                    category: 'time',
                    dueDateClass: '',
                    start: new Date(response[i].start + 'Z'),
                    end: new Date(response[i].end + 'Z'),
                    bgColor: "#9bd912",
                    dragBgColor: "#9bd912",
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