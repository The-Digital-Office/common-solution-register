# User interface requirements

| Path | Contents |
|---|---|
| `wireframes/` | Wireframe sources (`*.dc.html`, `canvas.json`). They are the normative user interface requirements for the build (specification section 6.13). |
| `baseline/` | Approved wireframe images at 1280 pixels: the starting baselines for the visual comparison tests. |

The wireframes reference the design system stylesheet as an uploaded asset
(`/_blob/...`). In the build it is vendored under
`src/csr/static/vendor/sgds/4.3.0/` instead.

The baseline images were rendered from the wireframes by
[`tools/render-wireframes.js`](../tools/render-wireframes.js), using Playwright.
