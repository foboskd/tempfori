const url = new URL(window.location.href);
const operation_id = "operations-" + url.searchParams.get("operation");
const checkExist = setInterval(function () {
    if (document.getElementById(operation_id) != null) {
        clearInterval(checkExist);
        document.getElementById(operation_id).scrollIntoView();
    }
}, 100);
