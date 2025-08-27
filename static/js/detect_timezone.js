(function() {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (!tz) return;
    const current = document.cookie.split("; ").find(s => s.startsWith("user_timezone="))?.split("=")[1];
    if (current === encodeURIComponent(tz)) return;
    const attrs = ["path=/", "SameSite=Lax", "Max-Age=31536000"];
    if (location.protocol === "https:") attrs.push("Secure");
    document.cookie = `user_timezone=${encodeURIComponent(tz)}; ${attrs.join("; ")}`;
})();