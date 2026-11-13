# crowleyconsulting.ca

Website for **Noah Crowley Asbestos and Designated Substances Consulting** (legal name: Noah Crowley Consulting).
Plain HTML, CSS and JavaScript, hosted free on GitHub Pages. No build step is needed to publish.

## What's here

| Page | Purpose |
| --- | --- |
| `index.html` | Home: building owners, landlords, contractors, reports |
| `building-owners.html`, `landlords.html` | Building programs (Compliance Essentials, Project Ready, Facility Partner) |
| `contractors.html` | Cleared-to-Start Pass, the contractor compliance desk |
| `employers.html` | O. Reg. 490/09 duties; exposure monitoring not available yet (waits on a hygienist arrangement) |
| `obligation-check.html` | The Obligation Check quiz (routing rules from the business plan) |
| `services.html` | Report menu with public "from" prices |
| `asbestos-testing-*.html` | Local search pages: Windsor, Leamington, Chatham, Sarnia, London |
| `asbestos-testing-before-renovation.html` and three more | Trigger pages for search |
| `guide-*.html` | The four lead-magnet checklists |
| `about.html`, `contact.html`, `privacy.html`, `404.html` | Supporting pages |
| `assets/config.js` | **Your form and booking links go here** |
| `tools/build.py` | Regenerates every page from one place (copy and contact details). The site quotes only its public "from" prices |
| `tools/prices.json` | **The only place prices live.** The NCC price list, generated from the Price Guide and checked against it number by number. Never edit by hand |
| `tools/prices.py` | Fills the `[[tokens]]` in the copy from `prices.json`, and runs the two price guards on every build |

## Settings

Edit `assets/config.js` on GitHub (pencil icon) and commit:

```js
FORM_ENDPOINT: "https://formspree.io/f/xxxxxxx",   // where form submissions go
BOOKING_URL:   "https://calendly.com/your-link"    // where "Book a call" goes
```

Phone and email are written into every page for search engines. To change them, edit `SITE` at the top of
`tools/build.py` and run `python3 tools/build.py`, or ask Claude to rebuild with your details.

## Prices

Copy never types a price, percentage, turnaround or inclusion count. It writes a token such as `[[from.limited]]` or
`[[labDays]]`, and the build fills it from `tools/prices.json`. Every build then runs two guards and stops if either fails:

- **No typed prices:** `tools/build.py`, `assets/site.js` and `assets/ncc-rules.js` may not contain an NCC price or
  promise outside the documented `NOT_PRICES` list in `tools/prices.py` (fines, municipal fees, example lab results).
- **Nothing on the site the price list doesn't hold:** every price, percentage and turnaround on the built pages and
  `llms.txt` must be a value from `tools/prices.json`, and no token may be left unfilled.

To change a price: change the Price Guide first, then ask Claude to run the price change routine. It rebuilds the
price list, copies it here as `tools/prices.json`, rebuilds the site and opens the pull request.

