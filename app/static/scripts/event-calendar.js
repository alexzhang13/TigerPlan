/* Script for handling Events Calendar */
var calendarList = [];

/* List of scheduleIds */
var scheduleIds = [];
var nextId = 0;

function addCalendar(calendar) {
    calendarList.push(calendar);
}

const calendarId = "1";
let cal;

function renderTimeSelectionCalendar(calendarDivId) {
    if (!calendarDivId) {
        calendarDivId = "#calendar";
    }
    cal = new tui.Calendar(calendarDivId, {
        id: calendarId,
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
            console.log(e);
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

            console.log('Update schedule with id: ' + e.schedule.id);

            // prevent changes from overwriting calendarId
            // DOES NOT WORK WITHOUT
            if (changes && changes.calendarId) {
                delete changes.calendarId;
            }

            cal.updateSchedule(schedule.id, schedule.calendarId, changes);

            // refreshScheduleVisibility();
        },
        'beforeDeleteSchedule': function (e) {
            // UPDATE ON DB ON FLASK
            deleteSchedule(e);

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

function deleteSchedule(e) {
    console.log('beforeDeleteSchedule', e);
    const index = scheduleIds.indexOf(e.schedule.id);
    if (index > -1) {
        scheduleIds.splice(index, 1);
    }
    cal.deleteSchedule(e.schedule.id, e.schedule.calendarId);
}

function destroyTimeSelectionCalendar() {
    cal.destroy();
}

function getAllSchedules() {
    var schedules = [];
    for (let i = 0; i < scheduleIds.length; i++) {
        var schedule = cal.getSchedule(scheduleIds[i], calendarId);
        schedules.push(schedule);
    }
    return schedules;
}

function saveNewSchedule(scheduleData) {
    console.log("Saving " + scheduleData);
    var randomColor = Math.floor(Math.random() * 16777215).toString(16);
    var strId = nextId.toString();
    nextId += 1;
    var schedule = {
        id: strId,
        calendarId: calendarId,
        title: scheduleData.title,
        start: scheduleData.start,
        end: scheduleData.end,
        color: "#111111",
        bgColor: "#93ea7f",
        dragBgColor: "#93ea7f",
        borderColor: '#FDF8F3',
        category: 'time',
        location: scheduleData.location
    };

    cal.createSchedules([schedule]);
    scheduleIds.push(strId);
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

let request = null;
let variable = "does this work";

function createEventInvitations(eventId) {
    $(this).prop("disabled", true);
    let url = "cr_event_invitations/" + eventId;
    $.ajax({
        type: "POST",
        url: url,
        success: function (response) {
            console.log("Success");
            document.location.reload();
        }
    });
}

function deleteEvent(eventId) {
    let url = "/del_event/" + eventId;

    $.ajax({
        type: "POST",
        url: url,
        success: function (response) {
            console.log(response);
            if (response.success) {
                let html = "<div class='alert alert-success'>";
                html += "Event deleted!</div>"
                $("#eventCard" + eventId).html(html);

                setTimeout(function () {
                    $("#eventCard" + eventId).hide(1000);
                    setTimeout(function () {
                        $("#eventCard" + eventId).remove();
                    }, 1000);
                }, 3000);
                return;
            } else {
                let banner = $('<div>',
                    { text: "An error occured" });
                banner.addClass("alert alert-warning");
                banner.appendTo("#eventCreationResponse");

                $("#eventCard" + eventId).append(banner);
                setTimeout(function () {
                    banner.hide(1000);
                    setTimeout(function () {
                        banner.remove()
                    }, 1000);
                }, 3000);
                return;
            }
        },
        error: function (error) {
            console.log(error);
        }
    });
}

function showCreateEventCard(show) {
    if (show) {
        $("#createEventCard").show();
        $("#showCreateEventCardButton").hide();
        renderTimeSelectionCalendar();
    } else {
        $("#createEventCard").hide(500);
        $("#showCreateEventCardButton").show();
        destroyTimeSelectionCalendar();
    }
}

function makeNewEventCard(eventId, eventName, groupName) {
    let deleteButton = $('<button>', { text: "Delete Event" });
    deleteButton.attr("onclick", "deleteEvent(" + eventId + ")");
    let deleteLink = $('<a>');
    deleteLink.append(deleteButton);

    let createInvitesButton = $('<button>',
        { text: "Create Event Invitations" });
    let createInvitesLink = $('<a>');
    createInvitesButton.attr("onclick",
        "createEventInvitations(" + eventId + ")");
    createInvitesLink.append(createInvitesButton);
    // <a>
    //     <button onclick="createEventInvitations('')"> Create Event Invitations </button>
    // </a>

    let cardBody = $('<div>');
    cardBody.addClass("card-body");
    cardBody.append(deleteLink);
    cardBody.append(createInvitesLink);

    let cardHead = $('<div>');
    cardHead.addClass("card-header text-white bg-teal");
    cardHead.append(document.createTextNode("Event name: "));
    let eventNameStrong = $('<strong>', { text: eventName });
    cardHead.append(eventNameStrong);
    cardHead.append(document.createTextNode(" - Group: " + groupName));

    let card = $('<div>');
    card.attr({ class: "card mt-3 mb-3" })
    card.addClass("card mt-3 mb-3");
    card.attr("id", "eventCard" + eventId);
    card.append(cardHead);
    card.append(cardBody);

    $("#existingEvents").append(card);
}


function checkNewEventValidity(id, name, schedules) {
    if (!id || id.trim() === "") {
        return "Issue identifying associated group";
    }
    if (!name || name.trim() === "") {
        return "A name is required";
    }
    if (!schedules || schedules.length == 0) {
        return "At least one timeblock is required";
    }
    return "";
}

function createNewEvent() {
    let id = $('#NewEventGroupId :selected').val();
    let name = $('#NewEventName').val();
    let location = $('#NewEventLocation').val();
    let description = $('#NewEventDescription').val();
    let schedules = getAllSchedules();

    let validity = checkNewEventValidity(id, name, schedules);

    if (validity != "") {
        console.log(validity);

        let banner = $('<div>', { text: validity });
        banner.addClass("alert alert-warning");
        banner.appendTo("#eventCreationResponse");

        setTimeout(function () {
            banner.hide(1000);
            setTimeout(function () {
                banner.remove()
            }, 1000);
        }, 3000);
        return;
    }

    console.log("creating new event");

    let timeblocks = []
    for (let i = 0; i < schedules.length; i++) {
        let schedule = schedules[i];
        let timeblock = {};
        if (schedule.start && schedule.end) {
            timeblock.start = schedule.start;
            timeblock.end = schedule.end;
            timeblock.name = schedule.title;
        }
        timeblocks.push(timeblock);
    }

    let newEventData = {};
    newEventData.groupId = id;
    newEventData.name = name;
    newEventData.location = location;
    newEventData.description = description;
    newEventData.timeblocks = timeblocks;

    console.log(newEventData);
    let url = '/add_event'
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(newEventData),
        dataType: "json",
        success: function (response) {
            console.log(response);
            let banner;
            if (response.success) {
                banner = $('<div>', { text: "Success!" });
                banner.addClass("alert alert-success");
            } else {
                banner = $('<div>', {
                    text: response.message ?
                        response.message : "An error occured"
                });
                banner.addClass("alert alert-warning");
                banner.appendTo("#eventCreationResponse");

                setTimeout(function () {
                    banner.hide(1000);
                    setTimeout(function () {
                        banner.remove()
                    }, 1000);
                }, 3000);
                return;
            }
            banner.appendTo("#eventCreationResponse");

            setTimeout(function () {
                banner.hide(1000);
                setTimeout(function () {
                    banner.remove()
                }, 1000);
            }, 3000);

            $("createNewEventButton").prop("disabled", false);
            makeNewEventCard(response.newEventId,
                name, response.groupName);
            showCreateEventCard(false);
            $('#select-box').prop('selectedIndex', 0);
            $('#NewEventName').val('');
            $('#NewEventLocation').val('');
            $('#NewEventDescription').val('');
        },
        error: function (error) {
            console.log(error);
            let banner = $('<div>', { text: "An error occurred" });
            banner.addClass("alert alert-warning");
            banner.appendTo("#eventCreationResponse");
            setTimeout(function () {
                banner.hide(1000);
                setTimeout(function () {
                    banner.remove()
                }, 1000);
            }, 3000);
            $("createNewEventButton").prop("disabled", false);
        }
    });
    $("createNewEventButton").on('click', function () {
        $(this).prop("disabled", true);
    });
}

function setup() {
    console.log("Setting up page");
    $('#createNewEventButton').on('click', createNewEvent);
}

$('document').ready(setup);
