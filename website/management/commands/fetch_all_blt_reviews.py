"""
Management command to fetch all PRs and reviews from all BLT repositories.
This is a convenience command that wraps fetch_gsoc_prs for all BLT repos.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db.models import Count

from website.models import GitHubIssue, GitHubReview, Repo


class Command(BaseCommand):
    help = "Fetch all PRs and reviews from all OWASP-BLT repositories"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset pagination and fetch from the beginning",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output",
        )

    def handle(self, *args, **options):
        reset = options.get("reset", False)
        verbose = options.get("verbose", False)

        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("Fetching PRs and Reviews from BLT Repositories"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")

        # Get all BLT repos from database
        blt_repos = Repo.objects.filter(repo_url__icontains="OWASP-BLT")
        repo_count = blt_repos.count()

        if repo_count == 0:
            self.stdout.write(self.style.WARNING("No BLT repositories found in database!"))
            self.stdout.write("Please run 'check_owasp_projects' or add repos manually first.")
            return

        self.stdout.write(f"Found {repo_count} BLT repositories:")
        for repo in blt_repos:
            self.stdout.write(f"  - {repo.name}: {repo.repo_url}")
        self.stdout.write("")

        # Build repo list for fetch_gsoc_prs command
        repo_list = []
        for repo in blt_repos:
            # Extract owner/repo from URL
            # e.g., https://github.com/OWASP-BLT/BLT -> OWASP-BLT/BLT
            if "github.com" in repo.repo_url:
                parts = repo.repo_url.split("github.com/")[-1].strip("/")
                repo_list.append(parts)

        if not repo_list:
            self.stdout.write(self.style.ERROR("Could not extract repository names from URLs"))
            return

        repos_arg = ",".join(repo_list)
        self.stdout.write(f"Fetching from: {repos_arg}")
        self.stdout.write("")

        # Call fetch_gsoc_prs command
        cmd_options = {
            "repos": repos_arg,
            "reset": reset,
            "verbose": verbose,
        }

        try:
            call_command("fetch_gsoc_prs", **cmd_options)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error running fetch_gsoc_prs: {str(e)}"))
            return

        # Display results
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("Results Summary"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")

        # Count PRs
        total_prs = GitHubIssue.objects.filter(
            type="pull_request", is_merged=True, repo__repo_url__icontains="OWASP-BLT"
        ).count()
        self.stdout.write(f"Total merged PRs: {total_prs}")

        # Count reviews
        total_reviews = GitHubReview.objects.filter(
            pull_request__repo__repo_url__icontains="OWASP-BLT"
        ).count()
        reviews_with_contributor = GitHubReview.objects.filter(
            reviewer_contributor__isnull=False, pull_request__repo__repo_url__icontains="OWASP-BLT"
        ).count()
        self.stdout.write(f"Total reviews: {total_reviews}")
        self.stdout.write(f"Reviews with contributor: {reviews_with_contributor}")
        self.stdout.write("")

        # Show top reviewers
        self.stdout.write(self.style.SUCCESS("Top 10 Code Reviewers:"))
        leaderboard = (
            GitHubReview.objects.filter(
                reviewer_contributor__isnull=False,
                pull_request__repo__repo_url__icontains="OWASP-BLT",
            )
            .values("reviewer_contributor__name")
            .annotate(total_reviews=Count("id"))
            .order_by("-total_reviews")[:10]
        )

        for idx, entry in enumerate(leaderboard, 1):
            self.stdout.write(f"  {idx}. {entry['reviewer_contributor__name']}: {entry['total_reviews']} reviews")

        if not leaderboard:
            self.stdout.write("  No reviews found yet.")

        self.stdout.write("")

        # Show top PR contributors
        self.stdout.write(self.style.SUCCESS("Top 10 PR Contributors:"))
        pr_leaderboard = (
            GitHubIssue.objects.filter(
                type="pull_request",
                is_merged=True,
                contributor__isnull=False,
                repo__repo_url__icontains="OWASP-BLT",
            )
            .values("contributor__name")
            .annotate(total_prs=Count("id"))
            .order_by("-total_prs")[:10]
        )

        for idx, entry in enumerate(pr_leaderboard, 1):
            self.stdout.write(f"  {idx}. {entry['contributor__name']}: {entry['total_prs']} PRs")

        if not pr_leaderboard:
            self.stdout.write("  No PRs found yet.")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("Done! Visit /leaderboard/ to see the results"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
