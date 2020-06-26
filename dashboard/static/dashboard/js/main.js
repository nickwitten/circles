function addAlertHTML(message, type) {
    alert = $('<div/>')
        .addClass('alert alert-' + type)
        .text(message);
    close_btn = $('<a/>')
        .attr('href','#')
        .addClass('close fas fa-times')
        .attr('data-dismiss', 'alert')
        .attr('aria-label','close');
    alert.append(close_btn);
    $('.alert-container').append(alert);
}

