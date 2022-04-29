/* Script for handling Events Time Selection Calendar */

let selectedTimeblockId = null;

const detailCalendarId = "2";
let detailCal = null;

function renderDetailCalendar(isFinalized, calendarDivId) {
    if (detailCal != null) {
        destroyDetailCalendar();
    }

    if (isFinalized === null) {
        isFinalized = false;
    }
    if (!calendarDivId) {
        calendarDivId = "#calendar";
    }
    detailCal = new tui.Calendar(calendarDivId, {
        id: detailCalendarId,
        defaultView: 'week',
        taskView: false,
        isReadOnly: true,
        scheduleView: ['time']
    });

    detailCal.on({
        'clickMore': function (e) {
            console.log('clickMore', e);
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
            // console.log('afterRenderSchedule', e);
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

    if (!isFinalized) {
        detailCal.on({
            'clickSchedule': function (event) {

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
            }
        });
    }
}

function colorToHex(color) {
    var hexadecimal = color.toString(16);
    return hexadecimal.length == 1 ? "0" + hexadecimal : hexadecimal;
}

const blue = [68, 74, 198];
const red = [233, 109, 112];

function getHexColor(availability, numResponses) {
    if (numResponses === 0) {
        return "#f7349e";
    }
    let ratio = availability / numResponses;
    let redComp = parseInt(blue[0] + ratio * (red[0] - blue[0]));
    let greenComp = parseInt(blue[1] + ratio * (red[1] - blue[1]));
    let blueComp = parseInt(blue[2] + ratio * (red[2] - blue[2]));
    console.log(redComp, greenComp, blueComp)
    let str = "#" + colorToHex(redComp) + colorToHex(greenComp) + colorToHex(blueComp);
    console.log(str);
    return str;
}

function renderChosenTime(response) {
    if (detailCal === null) {
        return;
    }
    console.log(response);
    let chosenTime = response.chosenTime;
    var schedule = {
        id: chosenTime.id,
        title: response.eventName,
        calendarId: detailCalendarId,
        category: 'time',
        dueDateClass: '',
        start: chosenTime.start + 'Z',
        end: chosenTime.end + 'Z',
        bgColor: "#f7349e",
        color: "#000000"
    }
    detailCal.createSchedules([schedule]);
    detailCal.setDate(new Date(chosenTime.start + 'Z'));
}

function renderDetailTimeBlocks(response) {
    if (!detailCal) {
        return;
    }
    console.log(response);
    let eventTimes = response.responseTimes;
    let numResponses = response.numResponses;
    var eventTimesList = [];
    for (let i = 0; i < eventTimes.length; i++) {
        var d = {
            id: eventTimes[i].id,
            title: "Available: " + eventTimes[i].availability,
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
    if (detailCal) {
        detailCal.destroy();
        detailCal = null;
    }
    selectedTimeblockId = null;
}

function getSelectedTimeblockId() {
    return selectedTimeblockId;
}