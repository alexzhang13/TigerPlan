/* Script for handling Events Calendar */
var calendarList = [];

function addCalendar(calendar) {
    calendarList.push(calendar);
}

let recurringCal;
let onetimeCal;
const recurringCalId = "1";
const onetimeCalId = "2";
let recurring;
function renderEditConflictsCalendars() {
    if (recurring) {
        recurringCal = new tui.Calendar('#recurCalendar', {
            id: recurringCalId,
            defaultView: 'week',
            taskView: false,
            scheduleView: ['time'],
            useCreationPopup: true,
            useDetailPopup: true,
        });
        recurringCal.on({
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
                saveNewSchedule(e, true);
            },
            'beforeUpdateSchedule': function (e) {
                var schedule = e.schedule;
                var changes = e.changes;

                console.log('beforeUpdateSchedule', e);

                var data = {
                    id: schedule.id,
                    title: (e.changes && e.changes.title) ? e.changes.title : null,
                    start: (e.changes && e.changes.start) ? e.changes.start.toUTCString() : null,
                    end: (e.changes && e.changes.end) ? e.changes.end.toUTCString() : null,
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
                        recurringCal.updateSchedule(schedule.id, schedule.calendarId, changes);
                    },
                    error: function (error) {
                        console.log(error);
                    }
                });

                // UPDATE ON DB ON FLASK

                // refreshScheduleVisibility();
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

                        recurringCal.deleteSchedule(e.schedule.id, e.schedule.calendarId);
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
                    recurringCal.setTheme({
                        'week.daygridLeft.width': '77px',
                        'week.timegridLeft.width': '77px'
                    });
                } else {
                    recurringCal.setTheme({
                        'week.daygridLeft.width': '60px',
                        'week.timegridLeft.width': '60px'
                    });
                }

                return true;
            }

        });
    } else {
        onetimeCal = new tui.Calendar('#onetimeCalendar', {
            id: onetimeCalId,
            defaultView: 'week',
            taskView: false,
            scheduleView: ['time'],
            useCreationPopup: true,
            useDetailPopup: true,
        });
        onetimeCal.on({
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
                saveNewSchedule(e, false);
            },
            'beforeUpdateSchedule': function (e) {
                var schedule = e.schedule;
                var changes = e.changes;

                console.log('beforeUpdateSchedule', e);

                var data = {
                    id: schedule.id,
                    title: (e.changes && e.changes.title) ? e.changes.title : null,
                    start: (e.changes && e.changes.start) ? e.changes.start.toUTCString() : null,
                    end: (e.changes && e.changes.end) ? e.changes.end.toUTCString() : null,
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
                        onetimeCal.updateSchedule(schedule.id, schedule.calendarId, changes);
                    },
                    error: function (error) {
                        console.log(error);
                    }
                });

                // UPDATE ON DB ON FLASK

                // refreshScheduleVisibility();
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

                        onetimeCal.deleteSchedule(e.schedule.id, e.schedule.calendarId);
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
                    onetimeCal.setTheme({
                        'week.daygridLeft.width': '77px',
                        'week.timegridLeft.width': '77px'
                    });
                } else {
                    onetimeCal.setTheme({
                        'week.daygridLeft.width': '60px',
                        'week.timegridLeft.width': '60px'
                    });
                }

                return true;
            }

        });
    }
}

function saveNewSchedule(scheduleData, recurring) {
    var randomId = Math.floor(Math.random() * 22345679).toString(16);

    // figure out better ID genereation
    var schedule = {
        id: randomId,
        title: scheduleData.title,
        start: scheduleData.start,
        end: scheduleData.end,
        bgColor: recurring ? recurringColor : onetimeColor,
        dragBgColor: recurring ? recurringColor : onetimeColor,
        category: 'time',
        // category: scheduleData.isAllDay ? 'allday' : 'time',
        // dueDateClass: '',
        location: scheduleData.location,
        isRecurring: recurring
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
            if (recurring) {
                recurringCal.createSchedules([schedule]);
            } else {
                onetimeCal.createSchedules([schedule]);
            }
        },
        error: function (error) {
            console.log(error);
        }
    });
}


const recurringColor = "#9BD912";
function renderUserRecurringConflicts(conflicts) {
    if (!recurringCal) {
        return;
    }
    let allRenderedUserConflicts = [];
    let calStart = recurringCal.getDateRangeStart().toDate();
    let calEnd = recurringCal.getDateRangeEnd().toDate();
    calEnd.setDate(calEnd.getDate() + 1);
    console.log("Cal start", calStart);
    console.log("Cal end", calEnd);
    for (let i = 0; i < conflicts.length; i++) {
        let startTime = new Date(conflicts[i].start + 'Z');
        let endTime = new Date(conflicts[i].end + 'Z');
        startTime = getInRange(startTime, calStart, calEnd);
        endTime = getInRange(endTime, calStart, calEnd);
        var d = {
            id: conflicts[i].id,
            calendarId: recurringCalId,
            title: conflicts[i].name,
            category: 'time',
            dueDateClass: '',
            start: startTime,
            end: endTime,
            bgColor: recurringColor,
            dragBgColor: recurringColor,
            raw: "UserConflict"
        }
        allRenderedUserConflicts.push(d);
    }
    console.log(allRenderedUserConflicts);
    recurringCal.createSchedules(allRenderedUserConflicts);
}

const onetimeColor = "#12D3D9";
function renderUserOnetimeConflicts(conflicts) {
    if (!onetimeCal) {
        return;
    }
    let allRenderedUserConflicts = [];
    let calStart = onetimeCal.getDateRangeStart().toDate();
    let calEnd = onetimeCal.getDateRangeEnd().toDate();
    calEnd.setDate(calEnd.getDate() + 1);
    console.log("Cal start", calStart);
    console.log("Cal end", calEnd);
    for (let i = 0; i < conflicts.length; i++) {
        let startTime = new Date(conflicts[i].start + 'Z');
        let endTime = new Date(conflicts[i].end + 'Z');
        var d = {
            id: conflicts[i].id,
            calendarId: onetimeCalId,
            title: conflicts[i].name,
            category: 'time',
            dueDateClass: '',
            start: startTime,
            end: endTime,
            bgColor: onetimeColor,
            dragBgColor: onetimeColor,
            raw: "UserConflict"
        }
        allRenderedUserConflicts.push(d);
    }
    console.log(allRenderedUserConflicts);
    onetimeCal.createSchedules(allRenderedUserConflicts);
}

function loadUserConflicts() {
    let url = '/load_edit_conflicts'

    $.ajax({
        type: "GET",
        url: url,
        success: function (response) {
            if (!response.success) {
                console.log("An error occured");
            }
            console.log(response);
            if (recurring) {
                console.log("Recurring");
                renderUserRecurringConflicts(response.recurringConflicts);
            } else {
                console.log("One time");
                renderUserOnetimeConflicts(response.onetimeConflicts);
            }
        },
        error: function (error) {
            console.log(error);
        }
    });
}

function setRenderRangeText() {
    if (!onetimeCal) return;
    let start = onetimeCal.getDateRangeStart().toDate();
    let end = onetimeCal.getDateRangeEnd().toDate();
    let startString = (start.getMonth() + 1) + "/" + start.getDate() + "/" + start.getFullYear();
    let endString = (end.getMonth() + 1) + "/" + end.getDate() + "/" + end.getFullYear();
    let newRange = $('<span>', { text: startString + " ~ " + endString });
    $('#renderRange').empty();
    $("#renderRange").append(newRange);
}

$(document).ready(function () {
    const params = new Proxy(new URLSearchParams(window.location.search), {
        get: (searchParams, prop) => searchParams.get(prop),
    });
    // Get the value of "some_key" in eg "https://example.com/?some_key=some_value"
    if (params.type === "onetime") {
        recurring = false;
    } else {
        recurring = true;
    }
    renderEditConflictsCalendars();
    loadUserConflicts();
    $("#onetimeCalendarMenuPrev").on('click', function () {
        if (!onetimeCal) return;
        onetimeCal.prev();
        setRenderRangeText();
    });
    $("#onetimeCalendarMenuNext").on('click', function () {
        if (!onetimeCal) return;
        onetimeCal.next();
        setRenderRangeText();
    });
    setRenderRangeText();

    if (recurring) {
        $("#recurSpan").show();
        $("#onetimeButton").show();
        $("#onetimeButton").attr('href', '/editconflicts?type=onetime');
        $("#calendarType").html("Recurring");
        recurringCal.render();
    } else {
        $("#onetimeSpan").show();        
        $("#recurButton").show();
        $("#recurButton").attr('href', '/editconflicts?type=recur');
        $("#calendarType").html("One Time");
        onetimeCal.render();
    }
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