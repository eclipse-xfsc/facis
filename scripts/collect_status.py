#!/usr/bin/env python3
"""Collects health/status data for the FACIS root repo and its 6 component repos
from the GitHub REST API, and writes docs/status.json for the dashboard."""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

REPOS = [
    {"key": "root", "owner": "eclipse-xfsc", "repo": "facis", "label": "FACIS"},
    {"key": "dcs", "owner": "eclipse-xfsc", "repo": "facis-dcs", "label": "DCS"},
    {
        "key": "dcm",
        "owner": "eclipse-xfsc",
        "repo": "facis-fap-decentralized-catalogue-management",
        "label": "DCM",
    },
    {
        "key": "iot-ai",
        "owner": "eclipse-xfsc",
        "repo": "facis-fap-iot-ai",
        "label": "IoT & AI",
    },
    {
        "key": "partner-onboarding",
        "owner": "eclipse-xfsc",
        "repo": "facis-fap-partner-onboarding",
        "label": "Partner Onboarding",
    },
    {
        "key": "aviation-poc",
        "owner": "eclipse-xfsc",
        "repo": "facis-poc-federation-aviation",
        "label": "Aviation PoC",
    },
    {
        "key": "credential-issuance",
        "owner": "eclipse-xfsc",
        "repo": "facis-fap-principal-credential-issuance",
        "label": "Principal Credential Issuance",
    },
    {
        "key": "smart-deployment",
        "owner": "eclipse-xfsc",
        "repo": "smartdeployment",
        "label": "ESB",
    },
    {
        "key": "federated-catalogue",
        "owner": "eclipse-xfsc",
        "repo": "federated-catalogue",
        "label": "Federated Catalogue",
    },
]

TOKEN = os.environ.get("GITHUB_TOKEN")
STATUS_PATH = "dashboard/status.json"


def gh(path):
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
            "User-Agent": "facis-dashboard-script",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def parse_gh_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )


def days_since(date_str):
    if not date_str:
        return None
    return (datetime.now(timezone.utc) - parse_gh_date(date_str)).days


def load_previous():
    if not os.path.exists(STATUS_PATH):
        return {}
    try:
        with open(STATUS_PATH) as f:
            data = json.load(f)
        return {r["key"]: r for r in data.get("repos", []) if "key" in r}
    except Exception:
        return {}


def compute_trend(current, previous, goal):
    """goal: 'up' means higher is better (e.g. contributors), 'down' means lower is better (e.g. open issues)."""
    if current is None or previous is None:
        return None
    delta = current - previous
    if delta == 0:
        sentiment = "bad" if goal == "down" and current > 0 else "neutral"
        return {
            "previous": previous,
            "current": current,
            "delta": 0,
            "direction": "stable",
            "sentiment": sentiment,
        }

    direction = "up" if delta > 0 else "down"
    is_good = (direction == "up" and goal == "up") or (
        direction == "down" and goal == "down"
    )
    return {
        "previous": previous,
        "current": current,
        "delta": delta,
        "direction": direction,
        "sentiment": "good" if is_good else "bad",
    }


def collect_repo(entry, previous):
    owner, repo = entry["owner"], entry["repo"]
    info = gh(f"/repos/{owner}/{repo}")
    community = gh(f"/repos/{owner}/{repo}/community/profile")
    commits = gh(f"/repos/{owner}/{repo}/commits?per_page=1")
    contributors = gh(f"/repos/{owner}/{repo}/contributors?per_page=100&anon=1")
    runs = gh(f"/repos/{owner}/{repo}/actions/runs?per_page=30")
    issues = gh(f"/repos/{owner}/{repo}/issues?state=open&per_page=100")
    pulls = gh(f"/repos/{owner}/{repo}/pulls?state=open&per_page=100")
    releases = gh(f"/repos/{owner}/{repo}/releases?per_page=5")

    last_commit_date = None
    if commits and len(commits) > 0:
        last_commit_date = commits[0]["commit"]["committer"]["date"]

    def is_relevant_run(r):
        if r.get("event") == "schedule":
            return True
        return (r.get("actor") or {}).get("type") != "Bot"

    run_list = [r for r in (runs or {}).get("workflow_runs", []) if is_relevant_run(r)]

    last_run_status = run_list[0]["conclusion"] if run_list else None
    last_run_at = run_list[0]["created_at"] if run_list else None
    if run_list and last_run_status is None:
        last_run_status = "pending"

    one_day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_24h_runs = [
        r for r in run_list if parse_gh_date(r["created_at"]) >= one_day_ago
    ]

    latest_per_workflow_recent = {}
    for r in recent_24h_runs:
        wf_id = r.get("workflow_id")
        if wf_id not in latest_per_workflow_recent:
            latest_per_workflow_recent[wf_id] = r

    currently_failing_workflows = [
        r.get("name")
        for r in latest_per_workflow_recent.values()
        if r.get("conclusion") == "failure"
    ]

    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_runs = [
        r for r in run_list if parse_gh_date(r["created_at"]) >= one_week_ago
    ]
    recent_failures = sum(1 for r in recent_runs if r.get("conclusion") == "failure")
    today = datetime.now(timezone.utc).date()
    failures_by_day = [0] * 7
    for r in recent_runs:
        if r.get("conclusion") == "failure":
            run_date = parse_gh_date(r["created_at"]).date()
            day_index = max(0, min(6, 6 - (today - run_date).days))
            failures_by_day[day_index] += 1

    failed_run_details = [
        {
            "workflowName": r.get("name"),
            "branch": r.get("head_branch"),
            "date": r.get("created_at"),
            "url": r.get("html_url"),
        }
        for r in recent_runs
        if r.get("conclusion") == "failure"
    ]

    open_issues_only = [i for i in (issues or []) if "pull_request" not in i]
    human_open_prs = [
        p for p in (pulls or []) if (p.get("user") or {}).get("type") != "Bot"
    ]

    needs_review_prs = [
        p
        for p in human_open_prs
        if p.get("requested_reviewers") or p.get("requested_teams")
    ]

    contributor_count = len(contributors) if isinstance(contributors, list) else None
    open_issue_count = len(open_issues_only)

    governance_files = (community or {}).get("files") or {}
    keys = ["contributing", "license", "readme"]
    governance_score = sum(1 for k in keys if governance_files.get(k))

    if info is None:
        health = "unknown"
    elif last_run_status == "failure" or currently_failing_workflows:
        health = "red"  # the last relevant run failed, or another workflow is currently failing
    elif (
        last_run_status is None or recent_failures >= 2 or governance_score < len(keys)
    ):
        health = "yellow"  # currently passing, but recently unstable or has gaps
    else:
        health = "green"

    trends = {
        "contributorCount": compute_trend(
            contributor_count, (previous or {}).get("contributorCount"), goal="up"
        ),
        "openIssueCount": compute_trend(
            open_issue_count, (previous or {}).get("openIssueCount"), goal="down"
        ),
        "ciRecentFailureCount": compute_trend(
            recent_failures, (previous or {}).get("ciRecentFailureCount"), goal="down"
        ),
    }

    return {
        "key": entry["key"],
        "label": entry["label"],
        "owner": owner,
        "repo": repo,
        "url": (info or {}).get("html_url", f"https://github.com/{owner}/{repo}"),
        "exists": info is not None,
        "health": health,
        "lastCommitDate": last_commit_date,
        "daysSinceLastCommit": days_since(last_commit_date),
        "contributorCount": contributor_count,
        "ciLastRunStatus": last_run_status,
        "ciLastRunAt": last_run_at,
        "currentlyFailingWorkflows": currently_failing_workflows,
        "ciRecentFailureCount": recent_failures,
        "ciFailuresByDay": failures_by_day,
        "failedRuns": failed_run_details,
        "openIssueCount": open_issue_count,
        "openHumanPRCount": len(human_open_prs),
        "needsReviewPRCount": len(needs_review_prs),
        "releaseCount": releases and len(releases) or 0,
        "latestRelease": releases[0]["tag_name"] if releases else None,
        "governanceScore": governance_score,
        "governanceFiles": {
            "license": bool(governance_files.get("license")),
            "contributing": bool(governance_files.get("contributing")),
            "readme": bool(governance_files.get("readme")),
        },
        "trends": trends,
    }


def main():
    previous_map = load_previous()
    results = []
    for entry in REPOS:
        try:
            results.append(collect_repo(entry, previous_map.get(entry["key"])))
        except Exception as err:
            results.append(
                {
                    "key": entry["key"],
                    "label": entry["label"],
                    "owner": entry["owner"],
                    "repo": entry["repo"],
                    "error": str(err),
                }
            )

    output = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "repos": results,
    }
    os.makedirs("docs", exist_ok=True)
    with open(STATUS_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Wrote {STATUS_PATH} with {len(results)} repos")


if __name__ == "__main__":
    main()
