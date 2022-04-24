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

let reccuringUserConflicts = [];
let renderedRange = [0, 0];
let currentWeekOffset = 0;

// updates range, returns true if rendering is needed
function checkAndUpdateRange(newOffset) {
    if (newOffset < renderedRange[0]) {
        renderedRange[0] = newOffset;
        
        return true;
    } else if (newOffset > renderedRange[1]) {
        renderedRange[1] = newOffset;
        return true;
    }
    return false;
}

function calendarPrev() {
    if (!cal) {
        return;
    }
    currentWeekOffset -= 1;
    let render = checkAndUpdateRange(currentWeekOffset);
    if (render) {
        renderNewOffsets(currentWeekOffset);
    }
    cal.prev();
}

function calendarNext() {
    if (!cal) {
        return;
    }
    currentWeekOffset += 1;
    let render = checkAndUpdateRange(currentWeekOffset);
    if (render) {
        renderNewOffsets(currentWeekOffset);
    }
    cal.next();
}

function renderNewOffsets(offset) {
    if (!cal) {
        return;
    }

    let toCreate = [];

    for (let i = 0; i < reccuringUserConflicts.length; i++) {
        let origschedule = reccuringUserConflicts[i];
        let newStartTime = new Date(origschedule.start.getTime());
        let newEndTime = new Date(origschedule.end.getTime());
        newStartTime.setDate(newStartTime.getDate() + offset * 7);
        newEndTime.setDate(newEndTime.getDate() + offset * 7);
        let newSchedule = {
            title: origschedule.title,
            category: 'time',
            dueDateClass: '',
            start: newStartTime,
            end: newEndTime,
            bgColor: conflictColor,
            dragBgColor: conflictColor,
            raw: "UserConflict"
        }
        toCreate.push(newSchedule);
    }
    cal.createSchedules(toCreate);
}

function renderUserConflicts(response) {
    if (!cal) {
        return;
    }
    let allRenderedUserConflicts = [];
    let calStart = cal.getDateRangeStart().toDate();
    let calEnd = cal.getDateRangeEnd().toDate();
    calEnd.setDate(calEnd.getDate() + 1);
    console.log("Cal start", calStart);
    console.log("Cal end", calEnd);
    for (let i = 0; i < response.length; i++) {
        let startTime = new Date(response[i].start + 'Z');
        let endTime = new Date(response[i].end + 'Z');
        startTime = getInRange(startTime, calStart, calEnd);
        endTime = getInRange(endTime, calStart, calEnd);
        var d = {
            id: response[i].id,
            calendarId: '1',
            title: response[i].name,
            category: 'time',
            dueDateClass: '',
            start: startTime,
            end: endTime,
            bgColor: conflictColor,
            dragBgColor: conflictColor,
            raw: "UserConflict"
        }
        allRenderedUserConflicts.push(d);
        if (response[i].is_recurring) {
            reccuringUserConflicts.push(d);
        }
    }
    console.log(allRenderedUserConflicts);
    cal.createSchedules(allRenderedUserConflicts);
}

function renderEventTimeBlocks(eventTimes) {
    if (!cal) {
        return;
    }
    var eventTimesList = [];
    timeblockAvailabilities = {};
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
    if (eventTimesList[0] && eventTimesList[0].start) {
        cal.setDate(new Date(eventTimesList[0].start));
    }
}

function errorWhileFetchingTimeBlocks(error) {
    console.log(error);
}

function destroyInvitationCalendar() {
    if (cal) {
        cal.destroy();
        cal = null;
        timeblockAvailabilities = {};
    }
}

function getAllSelections() {
    return timeblockAvailabilities;
}

/********** HELPER FUNCTIONS: SHOULD BE MOVED TO UTILITIES **********/
function getInRange(dt, start, end) {
    if (dt < start) {
        let diff = daysBetween(dt, start);
        diff = Math.ceil(diff / 7) * 7;
        dt.setDate(dt.getDate() + diff);
    } else if (dt > end) {
        let diff = daysBetween(end, dt);
        diff = Math.ceil(diff / 7) * 7;
        dt.setDate(dt.getDate() - diff);
    }
    return dt;
}

function treatAsUTC(date) {
    let copy = new Date(date);
    copy.setMinutes(date.getMinutes() - date.getTimezoneOffset());
    return date;
}

function daysBetween(startDate, endDate) {
    var millisecondsPerDay = 24 * 60 * 60 * 1000;
    return (treatAsUTC(endDate) - treatAsUTC(startDate)) / millisecondsPerDay;
}

