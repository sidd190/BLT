# Leaderboard Implementation Summary

## Problem
The PR and Code Review leaderboards were showing "No data available" because they required UserProfile records (BLT user accounts), but most GitHub contributors don't have BLT accounts.

## Solution
Use the `Contributor` model to display ALL GitHub contributors, whether they have BLT accounts or not.

---

## Changes Made

### 1. Database Schema (`website/models.py`)
- Made `GitHubReview.reviewer` field **nullable** (optional)
- Added `reviewer_contributor` field to `GitHubReview` model
- Updated `__str__` method to handle both BLT users and external contributors

### 2. Migration (`website/migrations/0249_add_reviewer_contributor.py`)
- Alters `reviewer` field to be nullable
- Adds `reviewer_contributor` field

### 3. Management Commands

#### `fetch_gsoc_prs.py` (Recommended for complete coverage)
- ✅ Fetches **ALL PRs** from BLT repos (regardless of author)
- ✅ Fetches reviews from **ALL reviewers** (including non-BLT users)
- ✅ Auto-discovers BLT repos from database
- ✅ Creates `Contributor` records for both PR authors and reviewers

#### `update_github_issues.py` (Flexible)
- Fetches PRs **authored by BLT users** (users with GitHub profiles in system)
- ✅ With `--all-blt-repos` flag: Also fetches **ALL PRs from BLT repos**
- ✅ Fetches reviews from **ALL reviewers** (including non-BLT users)
- Creates `Contributor` records for both PR authors and reviewers
- Useful for comprehensive updates

### 4. Views (`website/views/user.py`)
- **PR Leaderboard**: Uses `contributor` field instead of `user_profile`
- **Code Review Leaderboard**: Uses `reviewer_contributor` field instead of `reviewer`
- **Dynamic filtering**: Uses `repo__repo_url__icontains="OWASP-BLT"` to automatically include any new BLT repos

### 5. Templates (`website/templates/leaderboard_global.html`)
- Displays contributor avatar, name, and GitHub URL
- Shows BLT username if they have an account
- Falls back to contributor name if no BLT account

---

## How to Fetch All Reviews

### ⭐ Recommended: Use `fetch_gsoc_prs` for complete coverage

### Option 1: Fetch reviews for all BLT repos (Recommended)
```bash
docker-compose exec app python manage.py fetch_gsoc_prs --reset
```

When run without `--repos` argument, this command automatically:
- Discovers all OWASP-BLT repos from the database
- Fetches PRs and reviews from all of them
- Falls back to GSOC25_PROJECTS if no repos found in database

### Option 2: Fetch reviews for specific repo(s)
```bash
docker-compose exec app python manage.py fetch_gsoc_prs --repos="OWASP-BLT/BLT" --reset
```

Or multiple repos:
```bash
docker-compose exec app python manage.py fetch_gsoc_prs --repos="OWASP-BLT/BLT,OWASP-BLT/BLT-Flutter" --reset
```

### Option 3: Fetch reviews for BLT users' PRs + all BLT repo PRs
```bash
docker-compose exec app python manage.py update_github_issues --all-blt-repos
```

This command:
1. First fetches PRs from BLT users (users with GitHub profiles)
2. Then fetches ALL PRs from BLT repos (including non-BLT users)
3. Fetches reviews from all reviewers

Or fetch only BLT users' PRs:
```bash
docker-compose exec app python manage.py update_github_issues
```

---

## Key Features

✅ **Dynamic repo filtering** - Automatically includes any new OWASP-BLT repos added to database
✅ **Works for all contributors** - No BLT account required
✅ **Backward compatible** - Still shows BLT usernames when available
✅ **Bot filtering** - Automatically skips bot accounts (e.g., coderabbitai[bot])
✅ **Incremental updates** - Commands can be run multiple times without duplicating data

---

## Verification

Check if reviews are being stored:
```bash
docker-compose exec app python manage.py shell -c "
from website.models import GitHubReview
from django.db.models import Count

print('Total reviews:', GitHubReview.objects.count())
print('Reviews with reviewer_contributor:', GitHubReview.objects.filter(reviewer_contributor__isnull=False).count())

# Check leaderboard
leaderboard = GitHubReview.objects.filter(
    reviewer_contributor__isnull=False,
    pull_request__repo__repo_url__icontains='OWASP-BLT',
).values('reviewer_contributor__name').annotate(total_reviews=Count('id')).order_by('-total_reviews')[:10]

print('\nTop 10 reviewers:')
for entry in leaderboard:
    print(f\"  {entry['reviewer_contributor__name']}: {entry['total_reviews']} reviews\")
"
```

---

## Next Steps

1. Run migration: `docker-compose exec app python manage.py migrate`
2. Fetch reviews: Run one of the commands above
3. Visit `/leaderboard/` to see the results!
