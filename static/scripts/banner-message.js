function displayMessage(message, messageType) {
    let messageObject = $(`<div class="message message--${messageType}" style="display: none">${message}</div>`);
    $("body").append(messageObject);
    messageObject.slideDown();
    setTimeout(function () {
        messageObject.slideUp(400, function () {
            messageObject.remove();
        });
    }, 5000);
}
