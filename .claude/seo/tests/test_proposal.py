import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import proposal


class ProposalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name) / 'site'
        self.root.mkdir()
        def git(*args):
            return subprocess.run(['git', '-C', str(self.root), *args], check=True,
                                  capture_output=True, text=True).stdout.strip()
        self.git = git
        git('init', '-q', '-b', 'main')
        git('config', 'user.name', 'Test')
        git('config', 'user.email', 'test@example.com')
        (self.root / 'index.html').write_text('Old unverified claim\n')
        git('add', 'index.html')
        git('commit', '-qm', 'baseline')
        (self.root / 'index.html').write_text('Check current details\n')
        self.patch = pathlib.Path(self.tmp.name) / 'change.patch'
        self.patch.write_text(git('diff', '--', 'index.html') + '\n')
        git('restore', 'index.html')
        self.reports = self.root / 'seo-reports'
        (self.reports / 'data').mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def ledger(self, status='verified'):
        (self.reports / 'data/findings-ledger.json').write_text(json.dumps({
            'next_id': 2, 'findings': [{'id': 'F-0001', 'status': status,
                'claim': 'Unverified property claim', 'evidence': 'owner unable to confirm'}]}))

    def test_rejects_unverified_finding_without_creating_branch(self):
        self.ledger('open')
        with self.assertRaisesRegex(ValueError, 'verified'):
            proposal.prepare('F-0001', self.patch, self.root, self.reports, '2026-10-04')
        self.assertNotIn('seo/proposals-2026-10-04', self.git('branch', '--list'))

    def test_creates_review_branch_and_keeps_main_unchanged(self):
        self.ledger()
        branch, path = proposal.prepare('F-0001', self.patch, self.root, self.reports, '2026-10-04')
        self.assertEqual(branch, 'seo/proposals-2026-10-04')
        self.assertEqual((self.root / 'index.html').read_text(), 'Old unverified claim\n')
        self.assertEqual((path / 'index.html').read_text(), 'Check current details\n')
        self.assertIn('Needs owner approval', (path / 'seo-reports/proposals/2026-10-04-F-0001.md').read_text())
        self.assertEqual(self.git('status', '--porcelain'), '?? seo-reports/')

    def test_rejects_patch_to_credentials_or_deploy_script(self):
        self.ledger()
        self.patch.write_text('diff --git a/api/secrets.php b/api/secrets.php\n')
        with self.assertRaisesRegex(ValueError, 'forbidden'):
            proposal.prepare('F-0001', self.patch, self.root, self.reports, '2026-10-04')

    def test_rejects_patches_to_executable_checks_and_casefolded_secrets(self):
        self.ledger()
        for path in ('.claude/seo/verify.sh', 'scripts/other.sh', '.ENV'):
            with self.subTest(path=path):
                self.patch.write_text(f'diff --git a/{path} b/{path}\n')
                with self.assertRaisesRegex(ValueError, 'forbidden'):
                    proposal.prepare('F-0001', self.patch, self.root, self.reports, '2026-10-04')

    def test_failed_verification_restores_clean_proposal_worktree(self):
        self.ledger()
        check = self.root / '.claude/seo/verify.sh'
        check.parent.mkdir(parents=True)
        check.write_text('#!/bin/sh\nexit 1\n')
        check.chmod(0o755)
        self.git('add', '.claude/seo/verify.sh')
        self.git('commit', '-qm', 'verifier')
        with self.assertRaisesRegex(ValueError, 'verification failed'):
            proposal.prepare('F-0001', self.patch, self.root, self.reports, '2026-10-04')
        path = self.root.parent / 'site-proposals-2026-10-04'
        self.assertEqual(subprocess.run(['git', '-C', str(path), 'status', '--porcelain'],
                                        capture_output=True, text=True).stdout, '')
        self.assertEqual((path / 'index.html').read_text(), 'Old unverified claim\n')

    def test_whitespace_error_in_patch_restores_clean_worktree(self):
        self.ledger()
        (self.root / 'index.html').write_text('Check current details \nsecond line\n')
        self.patch.write_text(self.git('diff', '--', 'index.html') + '\n')
        self.git('restore', 'index.html')
        with self.assertRaisesRegex(ValueError, 'diff --check'):
            proposal.prepare('F-0001', self.patch, self.root, self.reports, '2026-10-04')
        path = self.root.parent / 'site-proposals-2026-10-04'
        self.assertEqual(subprocess.run(['git', '-C', str(path), 'status', '--porcelain'],
                                        capture_output=True, text=True).stdout, '')
        self.assertEqual((path / 'index.html').read_text(), 'Old unverified claim\n')


if __name__ == '__main__':
    unittest.main()
