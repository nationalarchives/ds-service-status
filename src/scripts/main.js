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

// const rtf1 = new Intl.RelativeTimeFormat("en", {
//   localeMatcher: "best fit",
//   numeric: "always",
//   style: "long",
// });

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
