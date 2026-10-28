# Coverage (2026-10-29 @ fd29588)

Status per topic: `documented`, `unknown: <question for the owner>`, `not applicable: <reason>`.

| Topic | Status |
|---|---|
| OVERVIEW | documented |
| STACK | unknown: which PHP version does Hostinger run in production? |
| STRUCTURE | documented |
| COMMANDS | documented |
| ARCHITECTURE | documented |
| CONVENTIONS | documented |
| ENVIRONMENT | unknown: is the hPanel cron for `reconcile-pending.php` set up, and at what interval? |
| TESTING | documented |
| DECISIONS | unknown: should `blogs/*.md` (14 unused files) be retired? |
| GOTCHAS | documented |
| STATUS | documented |
| FLOWS/booking | documented |
| FLOWS/cancellation | unknown: has a paid cancellation been tested end to end against live eZee? |
| FLOWS/payment-recovery | documented |
| FLOWS/content-publish | documented |
| FLOWS/weekly-seo | documented |
| DATA | unknown: is `bookings.log` ever rotated or pruned, and how large is it? |
| API | documented |
| INTEGRATIONS | unknown: are the production Razorpay keys live or test? |
| AUTH | unknown: who besides the owner holds hPanel, eZee, Razorpay and Google console access? |
| JOBS | documented |
| DEPLOY | unknown: who is the DNS provider/registrar, and is there any rollback beyond redeploying an old file? |
| RUNBOOKS | documented |
| GLOSSARY | documented |
| OBSERVABILITY | unknown: is there any uptime monitor or PHP error-log check? |
| EXTERNAL | unknown: is there a ticket tracker or other owner/on-call contact? |
