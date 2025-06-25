# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.3.x   | :white_check_mark: |
| 0.2.x   | :x:                |
| 0.1.x   | :x:                |
| < 0.1   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them responsibly using one of the following methods:

### 🔒 Private Vulnerability Reporting (Recommended)

Use GitHub's private vulnerability reporting feature:

1. Go to the [Security tab](https://github.com/Bugsterapp/bugster-cli/security) of this repository
2. Click "Report a vulnerability"
3. Fill out the vulnerability report form with as much detail as possible

### 📧 Email Reporting

Send vulnerability reports to: **ignacio@bugster.dev**

Please include the following information in your report:

- **Type of issue** (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- **Full paths** of source file(s) related to the manifestation of the issue
- **Location** of the affected source code (tag/branch/commit or direct URL)
- **Special configuration** required to reproduce the issue
- **Step-by-step instructions** to reproduce the issue
- **Proof-of-concept or exploit code** (if possible)
- **Impact** of the issue, including how an attacker might exploit it

### 🕒 Response Timeline

We aim to respond to security vulnerability reports according to the following timeline:

- **Initial Response**: Within 24 hours of receiving the report
- **Assessment**: Within 72 hours, we'll provide an initial assessment
- **Updates**: We'll provide regular updates every 7 days until resolution
- **Resolution**: Critical vulnerabilities will be patched within 30 days
- **Disclosure**: Coordinated disclosure will occur after a fix is available

### 🛡️ Vulnerability Assessment Process

1. **Triage**: We assess the severity and impact of the reported vulnerability
2. **Verification**: We reproduce the issue in our development environment
3. **Classification**: We classify the vulnerability using CVSS 3.1 scoring
4. **Fix Development**: We develop and test a fix for the vulnerability
5. **Release**: We release a patch and security advisory
6. **Disclosure**: We coordinate public disclosure with the reporter

### 🏆 Security Researcher Recognition

We value the security research community's contributions to keeping Bugster CLI secure. Security researchers who responsibly disclose vulnerabilities may be:

- **Acknowledged** in our security advisories and release notes
- **Listed** in our security researchers hall of fame (with permission)
- **Invited** to participate in our security advisory process

### 📋 Scope

This security policy covers the following components:

#### ✅ In Scope
- **Bugster CLI core application** (`bugster/` directory)
- **Command-line interface** and argument parsing
- **Configuration handling** and file operations
- **Network communications** with Bugster API
- **Authentication mechanisms** and API key handling
- **File system operations** and temporary file handling
- **Dependency vulnerabilities** in production dependencies
- **Installation scripts** and distribution packages

#### ❌ Out of Scope
- **Third-party services** (GitHub, Playwright, Node.js runtime)
- **Development dependencies** not included in production builds
- **Social engineering attacks** against Bugster team members
- **Physical attacks** against Bugster infrastructure
- **Denial of service attacks** against public services
- **Issues requiring physical access** to a user's machine

### 🚨 Severity Classification

We use the following severity levels based on CVSS 3.1:

#### 🔴 Critical (9.0-10.0)
- Remote code execution
- Privilege escalation to system administrator
- Complete system compromise

#### 🟠 High (7.0-8.9)
- Authentication bypass
- Sensitive data exposure
- Local privilege escalation

#### 🟡 Medium (4.0-6.9)
- Cross-site scripting (XSS)
- Information disclosure
- Denial of service

#### 🟢 Low (0.1-3.9)
- Minor information disclosure
- Low-impact denial of service
- Security configuration issues

### 🔧 Security Best Practices for Users

To help keep your Bugster CLI installation secure:

#### 🔐 API Key Security
- **Never commit API keys** to version control
- **Use environment variables** or secure configuration files
- **Rotate API keys regularly** (every 90 days recommended)
- **Restrict API key permissions** to minimum required scope

#### 🏠 Local Environment
- **Keep Bugster CLI updated** to the latest version
- **Verify downloads** from official sources only
- **Use latest Python and Node.js** versions when possible
- **Run with minimum required privileges**

#### 🌐 Network Security
- **Use HTTPS endpoints** for all API communications
- **Verify TLS certificates** are properly validated
- **Use secure networks** for CLI operations
- **Consider VPN usage** in untrusted environments

#### 📁 File System Security
- **Protect configuration files** with appropriate file permissions
- **Regularly audit test files** for sensitive data
- **Use secure temporary directories**
- **Clean up generated files** containing sensitive information

### 🚫 What NOT to Report

The following issues are **not considered security vulnerabilities**:

- **Bugs without security implications**
- **Feature requests**
- **Issues in development/testing dependencies**
- **User interface inconsistencies**
- **Performance issues**
- **Rate limiting or quota enforcement**
- **Issues requiring physical access to the device**
- **Vulnerabilities in third-party services we don't control**

---

## 🙏 Acknowledgments

We would like to thank the following security researchers for their responsible disclosure of vulnerabilities:

<!-- This section will be updated as vulnerabilities are reported and fixed -->

*No security vulnerabilities have been reported to date.*

---

**Last Updated**: June 2025
**Policy Version**: 1.0

For questions about this security policy, contact us at ignacio@bugster.dev
