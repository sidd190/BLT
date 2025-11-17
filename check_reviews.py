#!/usr/bin/env python
"""Quick script to check GitHubReview data"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blt.settings')
django.setup()

from website.models import GitHubReview, GitHubIssue, Contributor

print("=" * 60)
print("CHECKING GITHUB REVIEW DATA")
print("=" * 60)

# Check total reviews
total_reviews = GitHubReview.objects.count()
print(f"\nTotal GitHubReview records: {total_reviews}")

# Check reviews with reviewer_contributor
reviews_with_contributor = GitHubReview.objects.filter(reviewer_contributor__isnull=False).count()
print(f"Reviews with reviewer_contributor: {reviews_with_contributor}")

# Check reviews with reviewer (UserProfile)
reviews_with_user = GitHubReview.objects.filter(reviewer__isnull=False).count()
print(f"Reviews with reviewer (UserProfile): {reviews_with_user}")

# Check OWASP-BLT reviews
owasp_reviews = GitHubReview.objects.filter(
    pull_request__repo__repo_url__icontains="OWASP-BLT"
).count()
print(f"Reviews on OWASP-BLT repos: {owasp_reviews}")

# Check OWASP-BLT reviews with contributor
owasp_reviews_with_contributor = GitHubReview.objects.filter(
    reviewer_contributor__isnull=False,
    pull_request__repo__repo_url__icontains="OWASP-BLT"
).count()
print(f"OWASP-BLT reviews with reviewer_contributor: {owasp_reviews_with_contributor}")

# Show sample reviews
print("\n" + "=" * 60)
print("SAMPLE REVIEWS (first 5):")
print("=" * 60)
for review in GitHubReview.objects.select_related('reviewer_contributor', 'pull_request__repo')[:5]:
    print(f"\nReview #{review.review_id}")
    print(f"  Reviewer Contributor: {review.reviewer_contributor.name if review.reviewer_contributor else 'None'}")
    print(f"  Reviewer UserProfile: {review.reviewer.user.username if review.reviewer else 'None'}")
    print(f"  PR Repo: {review.pull_request.repo.name if review.pull_request.repo else 'None'}")
    print(f"  Repo URL: {review.pull_request.repo.repo_url if review.pull_request.repo else 'None'}")

# Check the leaderboard query
print("\n" + "=" * 60)
print("LEADERBOARD QUERY RESULT:")
print("=" * 60)
from django.db.models import Count

leaderboard = (
    GitHubReview.objects.filter(
        reviewer_contributor__isnull=False,
        pull_request__repo__repo_url__icontains="OWASP-BLT",
    )
    .values(
        "reviewer_contributor__name",
        "reviewer_contributor__github_url",
    )
    .annotate(total_reviews=Count("id"))
    .order_by("-total_reviews")[:10]
)

print(f"Leaderboard entries: {leaderboard.count()}")
for entry in leaderboard:
    print(f"  {entry['reviewer_contributor__name']}: {entry['total_reviews']} reviews")
