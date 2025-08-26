(function() {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (tz) {
        document.cookie = "user_timezone=" + tz + "; path=/";
    }
})();