#!/bin/bash
# Script to fetch all reviews from all BLT repos

echo "=========================================="
echo "Fetching PRs and Reviews from BLT Repos"
echo "=========================================="
echo ""

# Fetch from all BLT repos
docker-compose exec app python manage.py fetch_gsoc_prs \
  --repos="OWASP-BLT/BLT,OWASP-BLT/BLT-Flutter,OWASP-BLT/BLT-Bacon,OWASP-BLT/BLT-Action,OWASP-BLT/BLT-Extension" \
  --reset

echo ""
echo "=========================================="
echo "Checking Results"
echo "=========================================="
echo ""

# Check the results
docker-compose exec app python manage.py shell -c "
from website.models import GitHubReview, GitHubIssue
from django.db.models import Count

print('Total PRs:', GitHubIssue.objects.filter(type='pull_request', is_merged=True).count())
print('Total Reviews:', GitHubReview.objects.count())
print('Reviews with reviewer_contributor:', GitHubReview.objects.filter(reviewer_contributor__isnull=False).count())

# Check leaderboard
print('\n--- Code Review Leaderboard (Top 10) ---')
leaderboard = GitHubReview.objects.filter(
    reviewer_contributor__isnull=False,
    pull_request__repo__repo_url__icontains='OWASP-BLT',
).values('reviewer_contributor__name').annotate(total_reviews=Count('id')).order_by('-total_reviews')[:10]

for entry in leaderboard:
    print(f\"  {entry['reviewer_contributor__name']}: {entry['total_reviews']} reviews\")

print('\n--- PR Leaderboard (Top 10) ---')
pr_leaderboard = GitHubIssue.objects.filter(
    type='pull_request',
    is_merged=True,
    contributor__isnull=False,
    repo__repo_url__icontains='OWASP-BLT',
).values('contributor__name').annotate(total_prs=Count('id')).order_by('-total_prs')[:10]

for entry in pr_leaderboard:
    print(f\"  {entry['contributor__name']}: {entry['total_prs']} PRs\")
"

echo ""
echo "=========================================="
echo "Done! Visit /leaderboard/ to see results"
echo "=========================================="
