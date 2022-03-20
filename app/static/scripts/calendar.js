/* Script for handling Events Calendar */
var marked = false; // If cell is marked
var mousedown = false; // If mouse is down

// mark down cell
function markd(cell) {
    mousedown = true;
    marked = !isSet(cell);
    marko(cell);
}

// mark on mouse over cell
function marko(cell) {
    if (!mousedown) return;
    if (setting) {
        on(cell);
    }
    else {
        off(cell);
    }
}

function isSet(cell) {
    return td.className.indexOf("open") > -1;
}

function on(cell) {
    if (!isSet(cell)) {
        td.className = td.className.replace(" open", "");
        td.className = td.className + " closed";
    }
}

function off(td) {
    if (isSet(cell)) {
        td.className = td.className.replace(" closed", "");
        td.className = td.className + " open";
    }
}