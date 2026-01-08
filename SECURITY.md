# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by:

1. **Do NOT** open a public issue
2. Send an email to the repository maintainer via GitHub
3. Or use GitHub's private vulnerability reporting feature (Security tab → Report a vulnerability)

We will respond as quickly as possible and work with you to address the issue.

## Security Measures

This project implements the following security measures:

- **Non-root containers**: Docker images run as non-privileged user
- **Automated scanning**: Trivy vulnerability scanner runs on every build
- **SBOM generation**: Software Bill of Materials for supply chain transparency
- **Minimal permissions**: GitHub Actions use least-privilege principle
- **Pinned base images**: Reproducible builds with versioned dependencies

## Best Practices for Users

When deploying this application:

1. Always use the latest image version
2. Review Trivy scan results in the Security tab before deployment
3. Use environment-specific configurations
4. Keep Docker and Docker Compose up to date
5. Restrict network access to necessary ports only
6. Use volumes for sensitive data, not baked into images
