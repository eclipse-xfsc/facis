# How to submit

Pull Requests target the **eclipse-xfsc/facis** repository; every path below is relative to `Demonstrators/AI Challenge/`.

## Where
Your work lives in your track's folder:
```
tracks/<open|orce>/submissions/<your-name-or-pair>/
    README.md          what you built, how to run it, endpoint URL if deployed
    flow export        ORCE: exported flow tab JSON - Open: source code / app export
    result.json        one full response of your flow (trace + final_submission)
```

## Flow
1. Branch: `day1/<track>/<name>` (Day 2: `day2/<track>/<name>`).
2. Commit your submission folder.
3. Open a Pull Request titled `[<track>] <name> - day 1`.
4. Day-1 PRs are merged after the session and become the official baselines for Day 2.

## Rules
- Do not commit secrets or tokens. Endpoints run locally on your laptop; only the flow export, README and result.json enter the repo.
- Do not modify `data/` or `contracts/` - open an issue if something looks wrong.
- Keep your `result.json` honest: it must be the real output of a real run.
