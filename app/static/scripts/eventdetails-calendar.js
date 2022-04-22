/* Script for handling Events Time Selection Calendar */

let selectedTimeblockId = null;

const detailCalendarId = "2";
let detailCal = null;

function renderDetailCalendar(calendarDivId) {
    if (detailCal != null) {
        destroyDetailCalendar();
    }

    if (!calendarDivId) {
        calendarDivId = "#calendar";
    }
    detailCal = new tui.Calendar(calendarDivId, {
        id: detailCalendarId,
        defaultView: 'week',
        taskView: false,
        isReadOnly: true,
        scheduleView: ['time'],
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

    detailCal.on({
        'clickMore': function (e) {
            console.log('clickMore', e);
        },
        'clickSchedule': function (event) {
            console.log("clicked " + event.schedule.id);

            if (event.schedule.id == selectedTimeblockId) {
                selectedTimeblockId = null;
                detailCal.updateSchedule(event.schedule.id, detailCalendarId, {
                    isFocused: false
                });
            } else if (selectedTimeblockId == null) {
                selectedTimeblockId = event.schedule.id;
                detailCal.updateSchedule(event.schedule.id, detailCalendarId, {
                    isFocused: true
                });
            } else {
                detailCal.updateSchedule(selectedTimeblockId, detailCalendarId, {
                    isFocused: false
                });
                detailCal.updateSchedule(event.schedule.id, detailCalendarId, {
                    isFocused: true
                });
                selectedTimeblockId = event.schedule.id;
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
            console.log('afterRenderSchedule', e);
        },
        'clickTimezonesCollapseBtn': function (timezonesCollapsed) {
            console.log('timezonesCollapsed', timezonesCollapsed);

            if (timezonesCollapsed) {
                detailCal.setTheme({
                    'week.daygridLeft.width': '77px',
                    'week.timegridLeft.width': '77px'
                });
            } else {
                detailCal.setTheme({
                    'week.daygridLeft.width': '60px',
                    'week.timegridLeft.width': '60px'
                });
            }

            return true;
        }

    });
}

// const conflictColor = "#dddddd";
// const eventColorSelected = "#f7349e";
// const eventColorUnselected = "#ffe7ff";

function colorToHex(color) {
    var hexadecimal = color.toString(16);
    return hexadecimal.length == 1 ? "0" + hexadecimal : hexadecimal;
}

function convertRGBtoHex(red, green, blue) {
    return "#" + colorToHex(red) + colorToHex(green) + colorToHex(blue);
}
const blue = [68, 74, 198];
const red = [237, 66, 780];

function getHexColor(availability, numResponses) {
    console.log(numResponses)
    if (numResponses === 0) {
        return "#f7349e";
    }
    let ratio = availability/numResponses;
    let str = convertRGBtoHex(blue[0] + ratio * (red[0] - blue[0]), red[0] + ratio * (blue[0] - red[0]), blue[0] + ratio * (red[0] - blue[0]));
    console.log(str);
    return str;
}

function renderDetailTimeBlocks(response) {
    console.log(response);
    let eventTimes = response.responseTimes;
    let numResponses = response.numResponses;
    var eventTimesList = [];
    for (let i = 0; i < eventTimes.length; i++) {
        var d = {
            id: eventTimes[i].id,
            title: "Available Members: " + eventTimes[i].availability,
            calendarId: detailCalendarId,
            category: 'time',
            dueDateClass: '',
            start: eventTimes[i].start + 'Z',
            end: eventTimes[i].end + 'Z',
            bgColor: getHexColor(eventTimes[i].availability, numResponses),
            color: "#000000"
        }
        eventTimesList.push(d);
    }
    console.log(eventTimesList);
    detailCal.createSchedules(eventTimesList);
}

function destroyDetailCalendar() {
    detailCal.destroy();
    detailCal = null;
    selectedTimeblockId = null;
}

function getSelectedTimeblockId() {
    return selectedTimeblockId;
}