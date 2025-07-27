"""
GitHub PR creation service for Tiny Backspace.
This module handles creating pull requests with the generated changes.
"""

import os
import base64
from typing import List, Dict, Any, Optional
from github import Github, GithubException
from loguru import logger


class GitHubPRCreator:
    """Handles GitHub PR creation with generated changes."""
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
        if not self.github_token:
            logger.warning("GITHUB_TOKEN or GITHUB_PAT not set - PR creation will be disabled")
            self.github = None
        else:
            self.github = Github(self.github_token)
    
    async def create_pr_with_changes(
        self,
        repo_url: str,
        prompt: str,
        file_edits: List[Dict[str, str]],
        branch_name: str = None
    ) -> Dict[str, Any]:
        """
        Create a GitHub PR with the generated changes.
        
        Args:
            repo_url: GitHub repository URL
            prompt: Original user prompt
            file_edits: List of file edits to apply
            branch_name: Optional branch name (auto-generated if not provided)
            
        Returns:
            Dict with PR information or error details
        """
        if not self.github:
            return {
                "success": False,
                "error": "GitHub token not configured",
                "pr_url": None
            }
        
        try:
            # Parse repo URL to get owner and repo name
            owner, repo_name = self._parse_github_url(repo_url)
            
            # Get repository
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            
            # Generate branch name if not provided
            if not branch_name:
                branch_name = f"tiny-backspace-{self._generate_branch_suffix()}"
            
            # Create branch
            base_branch = repo.default_branch
            base_ref = repo.get_branch(base_branch)
            
            # Create new branch
            repo.create_git_ref(f"refs/heads/{branch_name}", base_ref.commit.sha)
            
            # Apply file edits
            commit_messages = []
            for edit in file_edits:
                file_path = edit["file_path"]
                new_content = edit["new_content"]
                description = edit.get("description", "Updated file")
                
                try:
                    # Check if file exists
                    try:
                        file = repo.get_contents(file_path, ref=branch_name)
                        # Update existing file
                        repo.update_file(
                            file_path,
                            f"Update {file_path}: {description}",
                            new_content,
                            file.sha,
                            branch=branch_name
                        )
                    except GithubException as e:
                        if e.status == 404:
                            # File doesn't exist, create it
                            repo.create_file(
                                file_path,
                                f"Add {file_path}: {description}",
                                new_content,
                                branch=branch_name
                            )
                        else:
                            raise
                    
                    commit_messages.append(f"Updated {file_path}")
                    
                except Exception as e:
                    logger.error(f"Error updating {file_path}: {str(e)}")
                    continue
            
            # Create pull request
            pr_title = f"🤖 AI-generated improvements: {prompt[:50]}..."
            pr_body = self._generate_pr_body(prompt, file_edits, commit_messages)
            
            pr = repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=base_branch
            )
            
            return {
                "success": True,
                "pr_url": pr.html_url,
                "pr_number": pr.number,
                "branch_name": branch_name,
                "files_updated": len(commit_messages)
            }
            
        except Exception as e:
            logger.error(f"Error creating PR: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "pr_url": None
            }
    
    def _parse_github_url(self, repo_url: str) -> tuple[str, str]:
        """Parse GitHub URL to extract owner and repo name."""
        # Handle different GitHub URL formats
        if repo_url.startswith("https://github.com/"):
            parts = repo_url.replace("https://github.com/", "").split("/")
            owner = parts[0]
            repo_name = parts[1].replace(".git", "")
        else:
            raise ValueError(f"Invalid GitHub URL: {repo_url}")
        
        return owner, repo_name
    
    def _generate_branch_suffix(self) -> str:
        """Generate a unique branch suffix."""
        import time
        import random
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        return f"{timestamp}-{random_suffix}"
    
    def _generate_pr_body(self, prompt: str, file_edits: List[Dict[str, str]], commit_messages: List[str]) -> str:
        """Generate PR description."""
        body = f"""## 🤖 AI-Generated Improvements

**Original Request:** {prompt}

### Changes Made

This PR contains AI-generated improvements based on your request:

"""
        
        for edit in file_edits:
            body += f"- **{edit['file_path']}**: {edit.get('description', 'Updated file')}\n"
        
        body += f"""
### Files Updated
{len(file_edits)} files were modified or created.

### Commits
"""
        
        for msg in commit_messages:
            body += f"- {msg}\n"
        
        body += """
---
*This PR was automatically generated by Tiny Backspace - an AI-powered coding assistant.*
"""
        
        return body


# Global instance
github_pr_creator = GitHubPRCreator() 