import {
  initAll,
  // Cookies,
} from "@nationalarchives/frontend/nationalarchives/all.mjs";

// const cookiesDomain =
//   document.documentElement.getAttribute("data-cookiesdomain");
// if (cookiesDomain) {
//   new Cookies({ domain: cookiesDomain });
// }

initAll();

const rtf1 = new Intl.RelativeTimeFormat("en", {
  localeMatcher: "best fit",
  numeric: "always",
  style: "long",
});

// const updateTimeElements = ($el) => {
//   const date = new Date($el.getAttribute("datetime"));
//   if (date) {
//     const secondsDifference = Math.round(
//       (date.getTime() - new Date().getTime()) / 1000,
//     );
//     let relativeTime = "Just now";

//     if (Math.abs(secondsDifference) >= 604800) {
//       relativeTime = rtf1.format(
//         Math.round(secondsDifference / 604800),
//         "week",
//       );
//     } else if (Math.abs(secondsDifference) >= 86400) {
//       relativeTime = rtf1.format(Math.round(secondsDifference / 86400), "day");
//     } else if (Math.abs(secondsDifference) >= 3600) {
//       relativeTime = rtf1.format(Math.round(secondsDifference / 3600), "hour");
//     } else if (Math.abs(secondsDifference) >= 60) {
//       relativeTime = rtf1.format(Math.round(secondsDifference / 60), "minute");
//     } else if (Math.abs(secondsDifference) > 5) {
//       relativeTime = rtf1.format(secondsDifference, "second");
//     }
//     $el.textContent = relativeTime;
//   }
// };

// document.querySelectorAll("time[datetime]").forEach(($el) => {
//   $el.setAttribute("title", $el.textContent);
//   updateTimeElements($el);
//   // setInterval(() => {
//   //   updateTimeElements($el);
//   // }, 1000);
// });

const $refreshWrapper = document.getElementById("refresh-wrapper");
const $refreshCheckbox = document.querySelector("input[name='refresh_page']");
const $refreshTimer = document.getElementById("refresh-countdown");

const updateRefreshTimer = (refreshTime) => {
  console.log("Updating refresh timer", refreshTime);
  if ($refreshTimer) {
    $refreshTimer.removeAttribute("hidden");
    const secondsDifference = Math.round(
      (refreshTime.getTime() - new Date().getTime()) / 1000,
    );
    if (secondsDifference <= 0) {
      $refreshTimer.textContent = "Page refreshing now...";
      window.location.reload();
    } else {
      $refreshTimer.textContent = `Next refresh ${rtf1.format(secondsDifference, "second")}...`;
    }
  }
};

if ($refreshWrapper && $refreshCheckbox && $refreshTimer) {
  $refreshWrapper.removeAttribute("hidden");
  $refreshCheckbox.addEventListener("change", (e) => {
    if (e.target.checked) {
      const url = new URL(window.location.href);
      url.searchParams.set("refresh", "true");
      window.location = url.toString();
    } else {
      const url = new URL(window.location.href);
      url.searchParams.delete("refresh");
      window.location = url.toString();
    }
  });

  if ($refreshCheckbox.checked) {
    const $generatedTimeEl = document.querySelector(
      "meta[name='tna.response.generated'",
    );
    if ($generatedTimeEl) {
      console.log("Found generated time meta tag", $generatedTimeEl);
      const generatedTime = new Date($generatedTimeEl.getAttribute("content"));
      if (generatedTime) {
        const refreshTime = new Date(
          generatedTime.getTime() + parseInt($refreshCheckbox.value) * 1000,
        );
        updateRefreshTimer(refreshTime);
        setInterval(() => {
          updateRefreshTimer(refreshTime);
        }, 1000);
      }
    }
  }
}
