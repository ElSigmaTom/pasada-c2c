# Host the PASADA judge demo on GitHub Pages

The project is ready for a normal GitHub **project Pages site**. No server or paid database is needed for the current demonstration. Keep the existing public Site as a backup link until the GitHub deployment has been verified.

## Publish

1. Create or choose the GitHub repository for this project. A suggested name is `pasada-c2c`. If using GitHub Free, use a public repository for Pages. Check the competition's source-disclosure requirements before choosing visibility.
2. Extract the new `PASADA_C2C_v20_GitHub.zip` (or the hosted `PASADA_GitHub_Pages.zip`; both contain the same source). Put its **contents** at the repository root: `.github/`, `dist/`, `package.json`, this guide, and the other source directories. Do not upload only the ZIP or place everything inside another enclosing folder. Preserve the hidden `.github` directory.
3. Commit/push to `main` or `master`. In the repository, open **Settings → Pages → Build and deployment → Source → GitHub Actions**.
4. Open **Actions → Publish PASADA demo → Run workflow** if the first push happened before Pages was enabled. The workflow runs the software checks, validates project-relative asset paths, then publishes only `dist/`.
5. Wait for the deploy job to finish. Use the actual URL from its `github-pages` environment/deployment output as the judges' link. GitHub project sites normally use `https://OWNER.github.io/REPOSITORY/`; that pattern is an example, not an already-created PASADA URL.

No repository was created and no GitHub Pages deployment was made while preparing this package. The destination repository has not been supplied. The connected repository search did not return PASADA. Do not claim that a prepared workflow is a running GitHub deployment.

## What judges can use

- **Control center**: interactive geographic map, play/pause, synthetic traffic/fault/emergency scenarios; clean geometry and satellite reference.
- **Installation**: signalized intersections in the 2/5/10 km catalog, editable lane templates, saved plans and individual component selection. Connect device invokes the browser's standard Web Serial chooser; firmware flashing remains deferred.
- **Emergency fleet**: browser-local vehicle registry and synthetic moving-beacon demonstration.
- **Tools & reference → Study results**: the completed reconstructed SUMO comparisons: 48 matched traffic-control runs and 78 emergency-beacon runs. Filters only inspect saved results; they do not rerun SUMO.
- **Public traffic data**: date/time and intersection filters with CSV/JSON exports for the explicitly synthetic sample archive.

The browser model, recorded SUMO evidence and public sample archive remain separately labeled. Recorded results are not a live cabinet/radio connection. The static website does not run native SUMO or an archive backend on GitHub Pages.

## Before sharing

Open the published GitHub link in a fresh browser session. Check the map at both regional and lane scales, both map views, play and emergency controls, saved-plan handoff, Study results filters and Public data downloads. Use a desktop browser for the full C2C. Web Serial needs a supporting browser and HTTPS; judges can inspect the installer without a physical board.

Plans and fleet edits are local to each browser and each origin. They do not synchronize between judges. Existing plans on the current Site will not automatically appear on GitHub because it is a different origin. To move your own plan, **Workspace → Export project** on the current site, then **Workspace → Import project / replay** on the GitHub site. Each judge starts from the bundled sample unless you deliberately distribute a reviewed project export.

Map tiles/imagery and Google fonts load from their existing providers and need internet access. Road context, application code, the traffic sample and compact study results are bundled. Leaflet/OpenStreetMap/Esri attributions are retained. Do not describe the package as an offline map.

GitHub deployment exposes the static content in `dist/`, including technical downloads already provided in the demo. It does not upload your browser's saved plans or fleet records. This export omits Sites identity, Git history, workspace files and credentials. Review any extra files you add separately.

## Source changes and rebuilds

For ordinary HTML/JS/CSS changes, commit the edited files in `dist/`; no framework build or npm dependency installation is needed. The workflow uses Node 22 for `npm test`, then runs the standard-library Python checks and link validation. Keep `dist/study/results.json` as the reviewed recorded release. Re-import from completed source packages only when a new reviewed evidence release is intentionally selected.

To refresh the downloadable repository package from source:

```bash
python tools/build_github_release.py
```

For a local web preview, serve `dist/` with an HTTP server. Opening `index.html` as `file://` does not support the app's module/fetch behavior. USB selection requires HTTPS or a secure localhost origin.

Official GitHub instructions:

- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

The workflow follows GitHub's documented configure-pages, upload-pages-artifact and deploy-pages route, with a `github-pages` environment and deployment permissions limited to the deploy job.

The static export includes all 126 compressed recorded study traces, native SUMO geometry and eight matched AM motion captures. **Study replays** needs no SUMO process or API server at runtime. MP4 evidence remains in Drive and is indexed in the AI Scratchpad.

Generated full-source ZIPs are omitted from this export to avoid bundling the same source twice. Technical handoff has been removed from the website. The development drawings, editable P1 KiCad ZIP and technical notes remain in the source package. The C2C app and all recorded replay data run from this repository.

The historical `PASADA_Chain_Draft_v0.1.zip` remains at the original host for existing links. The current hosted source export is `PASADA_GitHub_Pages.zip`, which contains the full current source and replay assets. Rebuild that export with `tools/build_github_release.py`; regenerating the legacy archive is unnecessary for publication.
