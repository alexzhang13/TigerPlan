async function loadEvents() {
    const start = dp.visibleStart();
    const end = dp.visibleEnd();
    const { data } = [
        {
            "id": "1",
            "text": "Calendar Event 1",
            "start": "2022-02-25T10:30:00",
            "end": "2022-02-25T16:30:00"
        },
        {
            "id": "2",
            "text": "Calendar Event 2",
            "start": "2022-02-24T09:00:00",
            "end": "2022-02-24T14:30:00"
        },
        {
            "id": "3",
            "text": "Calendar Event 3",
            "start": "2022-02-27T12:00:00",
            "end": "2022-02-27T16:00:00"
        }
    ];

    dp.update({
        events: data
    });
}

const dp = new DayPilot.Calendar("dp", {
    onEventMoved: async (args) => {
        const form = [
            { name: "Name", id: "text" }
        ];

        const modal = await DayPilot.Modal.form(form, args.e.data);
        if (modal.canceled) {
            return;
        }

        const data = {
            id: args.e.id(),
            newStart: args.newStart,
            newEnd: args.newEnd,
        };
        await DayPilot.Http.post(`backend_move.php`, data);
        console.log("The calendar event was moved.");

        dp.events.update({
            ...args.e.data,
            text: modal.result.text
        });
        console.log("The calendar event was updated.");
    }
});