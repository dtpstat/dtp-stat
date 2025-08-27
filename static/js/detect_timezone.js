(function() {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (tz) {
        const attrs = ["path=/", "SameSite=Lax", "Max-Age=31536000"]; // 1 year
        if (location.protocol === "https:") attrs.push("Secure");
            document.cookie = `user_timezone=${encodeURIComponent(tz)}; ${attrs.join("; ")}`;
    }
})();