/* Script for handling Events Calendar */
var marked = false; // If cell is marked
var mousedown = false; // If mouse is down

// mark down cell
function markd(cell) {
    mousedown = true;
    marked = !isOpen(cell);
    marko(cell);
}

// mark on mouse over cell
function marko(cell) {
    if (!mousedown) {
        popup(cell);
        return;
    }
    if (cell.className == "") return;
    if (!marked) {
        close(cell);
    }
    else {
        open(cell);
    }
}

// popup event window
function popup(cell) {
    console.log('Released');
}

function isOpen(cell) {
    return cell.className.indexOf("open") > -1;
}

function isClosed(cell) {
    return cell.className.indexOf("closed") > -1;
}

function close(cell) {
    if (isOpen(cell)) {
        cell.className = cell.className.replace(" open", "");
        cell.className = cell.className + " closed";
    }
}

function open(cell) {
    if (isClosed(cell)) {
        cell.className = cell.className.replace(" closed", "");
        cell.className = cell.className + " open";
    }
}

document.body.onmousedown = function () {
    mousedown = true;
}
document.body.onmouseup = function () {
    mousedown = false;
}