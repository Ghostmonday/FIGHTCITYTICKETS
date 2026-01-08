# Internal Data Retention Policy

**FightCityTickets.com**
**Document Classification:** Internal - Confidential
**Last Updated:** 2025-01-09
**Owner:** Operations

---

## Purpose

This document establishes data retention rules for FightCityTickets.com services. It ensures compliance with legal requirements, protects user privacy, and defines operational procedures for data handling, deletion, and response to data subject requests.

---

## Data Categories and Retention Periods

### 1. User Account Data

| Data Type | Retention Period | Reason | Deletion Method |
|-----------|-----------------|--------|-----------------|
| Email address | 2 years after last activity | Account recovery, communication | Automated + manual review |
| Name | 2 years after last activity | Service delivery | Automated + manual review |
| Physical address | 2 years after last activity | Service delivery, mailing | Automated + manual review |
| Phone number (optional) | 2 years after last activity | Account recovery | Automated + manual review |

### 2. Appeal Records

| Data Type | Retention Period | Reason | Deletion Method |
|-----------|-----------------|--------|-----------------|
| Citation number | 3 years | Legal defense, dispute resolution | Manual request required |
| Violation date/location | 3 years | Legal defense, dispute resolution | Manual request required |
| Vehicle information | 3 years | Legal defense, dispute resolution | Manual request required |
| Appeal letter content | 3 years | Legal defense, dispute resolution | Manual request required |
| User statements/narrative | 3 years | Legal defense, dispute resolution | Manual request required |

### 3. Payment Records

| Data Type | Retention Period | Reason | Deletion Method |
|-----------|-----------------|--------|-----------------|
| Transaction ID | 7 years | Tax compliance, PCI DSS | Archival (non-accessible) |
| Amount paid | 7 years | Tax compliance | Archival (non-accessible) |
| Stripe customer ID | 7 years | Payment processing | Stripe handles per their policy |
| Receipt history | 7 years | Tax compliance, audit | Archival (non-accessible) |

### 4. Evidence Data (Photos, Audio)

| Data Type | Retention Period | Reason | Deletion Method |
|-----------|-----------------|--------|-----------------|
| Uploaded photos | 1 year after appeal resolved | Customer service, disputes | Automated deletion |
| Voice recordings | 1 year after appeal resolved | Customer service, disputes | Automated deletion |
| Signature images | 1 year after appeal resolved | Verification, disputes | Automated deletion |

### 5. Technical/Operational Data

| Data Type | Retention Period | Reason | Deletion Method |
|-----------|-----------------|--------|-----------------|
| Server logs | 90 days | Security, debugging | Automated rotation |
| Access logs | 1 year | Security, compliance | Automated archival |
| Error logs | 30 days | Debugging | Automated deletion |
| Session data | Session end | Functionality | Automatic |

### 6. Communication Records

| Data Type | Retention Period | Reason | Deletion Method |
|-----------|-----------------|--------|-----------------|
| Support ticket history | 2 years | Customer service | Manual review |
| Email correspondence | 2 years | Legal protection | Manual review |
| Chat transcripts | 1 year | Customer service | Automatic |

---

## Data Deletion Procedures

### Automated Deletion (System-Implemented)

1. **Evidence Photos/Audio**
   - Trigger: 1 year after `appeal_resolved` timestamp
   - Method: Permanent deletion from storage (S3 buckets)
   - Verification: Log deletion event

2. **Technical Logs**
   - Trigger: Log age exceeds retention period
   - Method: Secure wipe (not just removal from index)
   - Verification: Log rotation records

3. **Session Data**
   - Trigger: Session timeout (24 hours inactivity)
   - Method: Session store expiration
   - Verification: Session audit logs

### Manual Deletion (Admin-Required)

1. **User Account Data**
   - Trigger: Valid deletion request from user
   - Approval: Operations lead
   - Method: Database deletion with backup retention
   - Verification: Deletion confirmation email

2. **Appeal Records**
   - Trigger: Valid deletion request from user
   - Approval: Operations lead + Legal review
   - Method: Anonymization (preserve transaction link, remove personal data)
   - Verification: Compliance audit trail

3. **Payment Records**
   - Trigger: Never (required by law)
   - Exception: Legal order requiring destruction
   - Method: Secure archival (offline, air-gapped)
   - Verification: Chain of custody documentation

---

## Data Subject Request Procedures

### Request Types

1. **Access Request**
   - User requests copy of all data held about them
   - Response time: 30 days
   - Data format: JSON export

2. **Correction Request**
   - User requests correction of inaccurate data
   - Response time: 30 days
   - Verification: Identity confirmation

3. **Deletion Request**
   - User requests data deletion
   - Response time: 30 days
   - Limitations: Payment records, legal holds

4. **Portability Request**
   - User requests data in portable format
   - Response time: 30 days
   - Format: JSON (standard, machine-readable)

### Request Handling Workflow

```
1. RECEIVE REQUEST
   └── Validate: Email, citation number, identity confirmation
   └── Log: Request ID, timestamp, request type

2. REVIEW REQUEST
   └── Check: Is request valid? (identity verified)
   └── Check: Are there legal holds?
   └── Check: What data can be deleted?

3. PROCESS REQUEST
   └── Execute: Appropriate deletion/correction/export
   └── Document: Chain of custody

4. RESPOND TO USER
   └── Confirm: Request completed
   └── Explain: What was done / what couldn't be done
   └── Document: Response sent

5. ARCHIVE
   └── Log: Request completion
   └── Retain: Request records per retention policy
```

---

## Legal Holds

### When a Legal Hold Applies

- Active litigation or threatened litigation
- Government investigation or inquiry
- Regulatory examination
- Internal investigation
- Intellectual property dispute

### Legal Hold Procedure

1. **Trigger**: Legal counsel or operations lead identifies need
2. **Notification**: IT, operations, customer service teams notified
3. **Freeze**: Automated deletion suspended for affected data
4. **Documentation**: Legal hold documented with:
   - Date hold placed
   - Scope of data affected
   - Reason for hold
   - Responsible party
5. **Release**: Hold released when no longer needed

---

## Third-Party Data Sharing

### Service Providers (Data Processors)

| Provider | Data Shared | Purpose | Agreement |
|----------|------------|---------|-----------|
| Stripe | Payment data, email | Payment processing | Data Processing Agreement |
| Lob | Appeal content, addresses | Mailing services | Data Processing Agreement |
| Cloud Provider | All service data | Hosting | Data Processing Agreement |
| AI Services | User statements | Statement refinement | Data Processing Agreement |

### Data Shared with Third Parties

- Only data necessary for service delivery
- No marketing or advertising data sharing
- No sale of personal data

### Third-Party Requests

- Subpoena: Escalate to legal counsel
- Warrant: Escalate to legal counsel
- Informal request: Require legal review
- Emergency request: Document, then review

---

## Compliance Checklists

### Daily Checks
- [ ] Monitor error logs for data access anomalies
- [ ] Verify backup completion
- [ ] Check automated deletion jobs status

### Weekly Checks
- [ ] Review access logs for suspicious activity
- [ ] Verify retention policy compliance
- [ ] Check pending data subject requests

### Monthly Checks
- [ ] Audit data access permissions
- [ ] Review third-party data sharing logs
- [ ] Update retention documentation as needed

### Quarterly Checks
- [ ] Full data inventory review
- [ ] Third-party agreement review
- [ ] Policy effectiveness assessment
- [ ] Staff training completion verification

---

## Incident Response

### Data Breach Procedures

1. **Detection**
   - Automated alerts (intrusion detection, access anomalies)
   - Manual reports (staff, users)

2. **Assessment**
   - Scope: What data affected?
   - Severity: Risk to individuals?
   - Notification requirement: 72 hours?

3. **Containment**
   - Isolate affected systems
   - Preserve evidence
   - Document timeline

4. **Notification**
   - Regulatory: As required by law
   - Affected individuals: As required by law
   - Internal: Management, legal

5. **Remediation**
   - Fix vulnerability
   - Reset credentials
   - Enhance monitoring

### Reporting Requirements

| Incident Type | Report To | Timeframe |
|---------------|-----------|-----------|
| Data breach (affecting users) | Legal counsel, regulators | 72 hours |
| Unauthorized access | Operations lead | 24 hours |
| Suspected fraud | Operations lead | 24 hours |
| System compromise | IT security | Immediate |

---

## Policy Review

### Review Schedule
- **Annual**: Full policy review
- **Quarterly**: Retention period review
- **As needed**: After significant changes

### Review Criteria
- Legal/regulatory changes
- Business process changes
- Incident findings
- Third-party relationship changes
- Technology changes

---

## Definitions

| Term | Definition |
|------|------------|
| Personal Data | Any information relating to an identified or identifiable natural person |
| Processing | Any operation performed on personal data |
| Data Subject | The individual whom data relates to |
| Data Processor | Third party processing data on our behalf |
| Legal Hold | Suspension of deletion procedures due to legal requirements |
| Deletion | Permanent removal of data (not just access removal) |
| Anonymization | Removal of personal identifiers (irreversible) |

---

## Contact

For questions about this policy:
- **Internal**: Operations Lead
- **External**: privacy@fightcitytickets.com

---

**Document Control**
- Version: 1.0
- Created: 2025-01-09
- Owner: Operations
- Classification: Internal - Confidential
- Distribution: Operations, Engineering, Legal