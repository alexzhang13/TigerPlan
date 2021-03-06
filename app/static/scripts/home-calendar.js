/* Script for handling Events Calendar */
var calendarList = [];

function addCalendar(calendar) {
    calendarList.push(calendar);
}

let cal;
function setUpHomeCalendar() {
    cal = new tui.Calendar('#calendar', {
        id: "1",
        defaultView: 'week',
        taskView: false,
        scheduleView: ['time'],
        isReadOnly: true,
        useCreationPopup: true,
        useDetailPopup: true
    });

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
            console.log('beforeCreateSchedule', e);
        },
        'beforeUpdateSchedule': function (e) {
            console.log('beforeUpdateSchedule', e);
        },
        'beforeDeleteSchedule': function (e) {
            console.log('beforeDeleteSchedule', e);
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

    addCalendar(cal);
}

const conflictColor = "#9bd912";
const eventColor = "#f7349e";

let reccuringUserConflicts = [];
let recurringUserEvents = [];
let renderedRange = [0, 0];
let currentWeekOffset = 0;

function setRenderRangeText() {
    if (!cal) return;
    let start = cal.getDateRangeStart().toDate();
    let end = cal.getDateRangeEnd().toDate();
    let startString = (start.getMonth() + 1) + "/" + start.getDate() + "/" + start.getFullYear();
    let endString = (end.getMonth() + 1) + "/" + end.getDate() + "/" + end.getFullYear();
    let newRange = $('<span>', { text: startString + " ~ " + endString });
    $('#renderRange').empty();
    $("#renderRange").append(newRange);
}

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
    setRenderRangeText();
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
    setRenderRangeText();
}

function renderNewOffsets(offset) {
    if (!cal) {
        return;
    }

    let toCreate = [];
    let newCalStart = new Date(calStart.getTime());
    let newCalEnd = new Date(calEnd.getTime());
    newCalStart.setDate(newCalStart.getDate() + offset * 7);
    newCalEnd.setDate(newCalEnd.getDate() + offset * 7);
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
            bgColor: origschedule.bgColor,
            dragBgColor: origschedule.dragBgColor,
            raw: "UserConflict"
        }
        toCreate.push(newSchedule);
    }

    for (let i = 0; i < recurringUserEvents.length; i++) {
        let origschedule = recurringUserEvents[i];
        console.log(origschedule.start);
        console.log(newCalEnd);
        if (origschedule.start < newCalEnd) {
            let newStartTime = new Date(origschedule.start.getTime());
            let newEndTime = new Date(origschedule.end.getTime());
            newStartTime = getInRange(newStartTime, newCalStart, newCalEnd);
            newEndTime = getInRange(newEndTime, newCalStart, newCalEnd);
            console.log(newStartTime);
            console.log(newEndTime);
            let newSchedule = {
                title: origschedule.title,
                category: 'time',
                dueDateClass: '',
                start: newStartTime,
                end: newEndTime,
                bgColor: origschedule.bgColor,
                dragBgColor: origschedule.dragBgColor,
                raw: "UserConflict"
            }
            toCreate.push(newSchedule);
        }

    }

    cal.createSchedules(toCreate);
}

let calStart;
let calEnd;
function renderUserConflicts(conflicts) {
    if (!cal) {
        return;
    }
    let allRenderedUserConflicts = [];
    calStart = cal.getDateRangeStart().toDate();
    calEnd = cal.getDateRangeEnd().toDate();
    calEnd.setDate(calEnd.getDate() + 1);
    console.log("Cal start", calStart);
    console.log("Cal end", calEnd);
    for (let i = 0; i < conflicts.length; i++) {
        let startTime = new Date(conflicts[i].start + 'Z');
        let endTime = new Date(conflicts[i].end + 'Z');
        if (conflicts[i].is_recurring) {
            let origDiff = endTime.getTime() - startTime.getTime();
            startTime = getInRange(startTime, calStart, calEnd);
            endTime.setTime(startTime.getTime() + origDiff);
        }
        var d = {
            id: conflicts[i].id,
            calendarId: '1',
            title: conflicts[i].name,
            category: 'time',
            dueDateClass: '',
            start: startTime,
            end: endTime,
            bgColor: conflictColor,
            dragBgColor: conflictColor,
            raw: "UserConflict"
        }
        allRenderedUserConflicts.push(d);
        if (conflicts[i].is_recurring) {
            reccuringUserConflicts.push(d);
        }
    }
    cal.createSchedules(allRenderedUserConflicts);
}

function renderEventTimes(events) {
    console.log(events);
    var toCreate = [];
    for (let i = 0; i < events.length; i++) {
        var d = {
            id: events[i].id,
            calendarId: '1',
            title: events[i].name,
            category: 'time',
            dueDateClass: '',
            start: new Date(events[i].start + 'Z'),
            end: new Date(events[i].end + 'Z'),
            bgColor: eventColor,
            dragBgColor: eventColor,
        }
        toCreate.push(d);
        if (events[i].is_recurring) {
            recurringUserEvents.push(d);
        }
    }
    cal.createSchedules(toCreate);
}

function loadUserConflicts() {
    let url = '/load_conflicts'

    $.ajax({
        type: "GET",
        url: url,
        success: function (response) {
            if (!response.success) {
                console.log("An error occured");
            }
            renderUserConflicts(response.conflicts);
            renderEventTimes(response.finalizedEvents);
        },
        error: function (error) {
            console.log(error);
        }
    });
}

$(document).ready(function () {
    setUpHomeCalendar();
    // call ajax to load calendar
    loadUserConflicts();
    $("#calendarMenuPrev").on('click', calendarPrev);
    $("#calendarMenuNext").on('click', calendarNext);
    setRenderRangeText();
});

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

