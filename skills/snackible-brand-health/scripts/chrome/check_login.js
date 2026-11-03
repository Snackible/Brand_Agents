// Sign-in check, run inside Claude in Chrome (javascript_tool) on an already loaded page.
// It says whether Chrome already holds a signed-in session for the site, so the agent can reuse it.
// It only reads whether a "Log in" prompt is showing. It never reads names, emails or cookies, and it
// never signs in: signing in is always done by the person.
//
// Returns JSON: {"site": "...", "signedIn": true | false | null, "evidence": "..."}
//   true  = no login prompt, account menu present: use the session
//   false = a login prompt or login wall is showing: record "needs_login" and move on
//   null  = unknown site or layout: treat as not confirmed and say so
(() => {
  const host = location.hostname.replace(/^www\./, "");
  const text = (document.body.innerText || "").slice(0, 600);
  const has = (re) => re.test(text);
  let site = host, signedIn = null, evidence = "unrecognised site";

  if (host.includes("instagram.com")) {
    site = "Instagram";
    const wall = has(/Log In/) && has(/Sign Up/) || /accounts\/login/.test(location.href);
    signedIn = !wall;
    evidence = wall ? "Log In / Sign Up shown in the page header" : "no login prompt in the header";
  } else if (host.includes("amazon.")) {
    site = "Amazon";
    const el = document.querySelector("#nav-link-accountList-nav-line-1");
    if (el) {
      signedIn = !/sign in/i.test(el.innerText);
      evidence = signedIn ? "account menu present" : 'header shows "Hello, sign in"';
    } else if (/ap\/signin/.test(location.href)) {
      signedIn = false;
      evidence = "redirected to the Amazon sign-in page";
    }
  } else if (host.includes("swiggy.com")) {
    site = "Swiggy Instamart";
    const wall = has(/Log in with phone number|Log in to continue/i);
    signedIn = !wall;
    evidence = wall ? "login prompt showing" : "no login prompt";
  } else if (host.includes("facebook.com")) {
    site = "Facebook / Meta Ad Library";
    signedIn = !has(/Log in|Log In/);
    evidence = signedIn ? "no login prompt" : "login prompt showing (the Ad Library itself does not need one)";
  }
  return JSON.stringify({ site, signedIn, evidence });
})()
