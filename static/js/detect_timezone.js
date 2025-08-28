(function() {
    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    if (!tz) return;
    const cookiePair = document.cookie
      .split(";")
      .map(s => s.trim())
      .find(s => s.startsWith("user_timezone="));
    const current = cookiePair
      ? cookiePair.split("=").slice(1).join("=")
      : undefined;
    if (current === encodeURIComponent(tz)) return;    const attrs = ["path=/", "SameSite=Lax", "Max-Age=31536000"];
    if (location.protocol === "https:") attrs.push("Secure");
    document.cookie = `user_timezone=${encodeURIComponent(tz)}; ${attrs.join("; ")}`;
})();