export type Difficulty = 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert'

export type Scenario = {
  id: number
  title: string
  sender: string
  channel: 'Email' | 'SMS'
  message: string
  explanation: string
  clues: string[]
  safe: boolean
}

export type Level = {
  key: Difficulty
  subtitle: string
  hint: string
  scenarios: Scenario[]
}

export const levels: Level[] = [
  {
    key: 'Beginner',
    subtitle: 'Clear red flags and obvious bait',
    hint: 'Check urgency language, suspicious links, and unusual payment requests.',
    scenarios: [
      {
        id: 1,
        title: 'Payroll Account Alert',
        sender: 'Payroll Security Team',
        channel: 'Email',
        message:
          'Hello employee, we detected an error while processing this month\'s salary deposit to your registered bank account. To prevent payroll suspension, confirm your account details within 30 minutes using payrol-secure-update.com. If you do not verify immediately, your payment may be delayed until next cycle.',
        explanation: 'Misspelled domain and artificial urgency are common phishing tactics.',
        clues: ['Misspelled domain name', 'Urgent deadline pressure'],
        safe: false,
      },
      {
        id: 2,
        title: 'Calendar Invite',
        sender: 'Operations Coordinator',
        channel: 'Email',
        message:
          'Hi team, the quarterly planning meeting has been moved from 11:00 AM to 2:00 PM due to a scheduling conflict with finance. Please confirm your attendance in the company calendar and review the same agenda deck shared last week before joining.',
        explanation: 'No pressure, no suspicious link, and normal internal context.',
        clues: ['Normal internal context', 'No request for credentials'],
        safe: true,
      },
      {
        id: 3,
        title: 'Contest Winner Notification',
        sender: 'Rewards Department',
        channel: 'Email',
        message:
          'Congratulations! Your email was selected in our annual student technology giveaway and you are eligible to receive a brand-new laptop at no cost. To release shipping and ownership transfer, submit your school login details before midnight or your prize will be reassigned to another participant.',
        explanation: 'Prize scams often use excitement and urgency to steal credentials.',
        clues: ['Too-good-to-be-true reward', 'Asks for login details to claim prize'],
        safe: false,
      },
      {
        id: 4,
        title: 'Library Return Reminder',
        sender: 'Campus Library',
        channel: 'SMS',
        message:
          'Campus Library reminder: the item currently borrowed on your account is due in 3 days. If you need more time, renew the item through the official campus app or at the circulation desk to avoid late fees.',
        explanation: 'Routine reminder with no suspicious link or sensitive information request.',
        clues: ['Expected service notification', 'Points to official app workflow'],
        safe: true,
      },
    ],
  },
  {
    key: 'Intermediate',
    subtitle: 'Mixed signals and social engineering',
    hint: 'Verify sender identity and cross-check links before you click.',
    scenarios: [
      {
        id: 1,
        title: 'Vendor Invoice Follow-up',
        sender: 'Vendor Accounts Desk',
        channel: 'Email',
        message:
          'Hi, this is the vendor accounting desk following up on outstanding invoices for this week. Please note we have updated our receiving bank account details effective immediately due to an internal audit migration. Use the attached banking sheet before processing pending payments today.',
        explanation: 'Unexpected bank detail change requests should always be validated out of band.',
        clues: ['Unexpected payment change', 'Attachment used for sensitive change'],
        safe: false,
      },
      {
        id: 2,
        title: 'HR Benefits Reminder',
        sender: 'Human Resources',
        channel: 'Email',
        message:
          'Friendly reminder from HR: open enrollment closes this Friday at 5:00 PM. Please review your benefits options through the official HR portal accessed from the employee intranet homepage. If you take no action, your current plan will remain active for next year.',
        explanation: 'Refers to official access path and avoids suspicious redirection.',
        clues: ['Uses official portal path', 'No external shortened link'],
        safe: true,
      },
      {
        id: 3,
        title: 'Cloud Storage Full Warning',
        sender: 'Cloud Platform Alerts',
        channel: 'Email',
        message:
          'Automatic storage warning: your cloud account is now at 99% capacity and critical files may be removed during nightly cleanup. To avoid deletion and service interruption, complete your upgrade now at cloud-storage-secure-check.net and confirm account ownership before the next backup window.',
        explanation: 'Threatening data loss and external lookalike domains are common phishing tactics.',
        clues: ['External lookalike domain', 'Fear-based pressure to act now'],
        safe: false,
      },
      {
        id: 4,
        title: 'Team Collaboration Invite',
        sender: 'Project Workspace Bot',
        channel: 'Email',
        message:
          'You were added to the Q2 delivery project board by your manager and assigned two starter tasks. Open the board from your standard company workspace dashboard to review deadlines, comment on tasks, and confirm your availability for sprint planning.',
        explanation: 'Message follows known process and does not push unknown links.',
        clues: ['Consistent with normal team process', 'No direct credential or payment request'],
        safe: true,
      },
    ],
  },
  {
    key: 'Advanced',
    subtitle: 'Personalized and contextual lures',
    hint: 'Watch for impersonation and unusual requests that use familiar context.',
    scenarios: [
      {
        id: 1,
        title: 'Friend Account Recovery Link',
        sender: 'Alex (Contact)',
        channel: 'SMS',
        message:
          'Hey, I\'m really stuck right now and support says they need one verified login from a trusted contact to unlock my account. Can you quickly sign in with your details on this page so they can confirm it\'s me? I need this done before class starts in 10 minutes.',
        explanation: 'Even trusted contacts can be compromised. Never enter credentials on shared links.',
        clues: ['Credential request via chat', 'Impersonation through familiar contact'],
        safe: false,
      },
      {
        id: 2,
        title: 'Campus IT Maintenance Notice',
        sender: 'Campus IT Services',
        channel: 'Email',
        message:
          'Campus IT notice: scheduled maintenance will begin tonight at 11:00 PM and should complete by 12:30 AM. During this window, email and portal access may be briefly unavailable. After maintenance, continue using your normal portal link and existing single sign-on process.',
        explanation: 'No sensitive data requested and it directs users to the standard portal workflow.',
        clues: ['Routine maintenance notice', 'Directs to usual access flow'],
        safe: true,
      },
      {
        id: 3,
        title: 'Scholarship Confirmation Form',
        sender: 'Student Aid Office',
        channel: 'SMS',
        message:
          'Hi, this is Student Aid with an urgent update on your scholarship file. Final approval is pending and must be completed today through tinyurl.com/aid-check. Please submit your student ID and bank account details so funds can be released before cutoff.',
        explanation: 'Shortened links and requests for financial data are major warning signs.',
        clues: ['Shortened URL hides destination', 'Requests sensitive financial information'],
        safe: false,
      },
      {
        id: 4,
        title: 'Admin Exam Schedule Update',
        sender: 'Academic Administration',
        channel: 'Email',
        message:
          'Academic Administration update: the final exam timetable has been revised for two departments due to room capacity changes. Please review the latest schedule in your existing student portal and confirm your exam dates, locations, and start times.',
        explanation: 'Informational update that routes users through a familiar official portal.',
        clues: ['No pressure language', 'References existing trusted portal'],
        safe: true,
      },
    ],
  },
  {
    key: 'Expert',
    subtitle: 'Advanced impersonation attempts',
    hint: 'Assume compromise unless sender, tone, and destination are all verifiable.',
    scenarios: [
      {
        id: 1,
        title: 'Executive Wire Request',
        sender: 'CEO Office',
        channel: 'SMS',
        message:
          'I need an immediate confidential transfer completed before the board call in the next 25 minutes. Do not involve finance or discuss this with the team yet, as this is highly sensitive. Send me confirmation and transaction details as soon as it is done.',
        explanation: 'Authority pressure + secrecy + money transfer is high-risk business email compromise behavior.',
        clues: ['Secrecy and urgency combined', 'Financial request without process'],
        safe: false,
      },
      {
        id: 2,
        title: 'Security Training Prompt',
        sender: 'Information Security Team',
        channel: 'SMS',
        message:
          'Security reminder: please complete this month\'s awareness training from your usual SSO dashboard before Friday. As always, IT and Security will never ask you for your password, verification code, or account credentials through SMS or chat.',
        explanation: 'Matches good security guidance and points users to trusted access workflow.',
        clues: ['Explicit safe behavior reminder', 'References standard SSO dashboard'],
        safe: true,
      },
      {
        id: 3,
        title: 'Legal Hold Confidential Notice',
        sender: 'Corporate Legal Affairs',
        channel: 'Email',
        message:
          'Due to an ongoing legal investigation, you are required to review a confidential file package immediately and acknowledge receipt before end of day. This matter is restricted, so do not inform colleagues or your manager at this stage. Sign in with your credentials here to access the documents securely.',
        explanation: 'Combines authority, secrecy, and credential harvesting in one message.',
        clues: ['Demands secrecy from colleagues', 'Requests credentials through message link'],
        safe: false,
      },
      {
        id: 4,
        title: 'Security Team Incident Bulletin',
        sender: 'SOC Incident Desk',
        channel: 'SMS',
        message:
          'SOC bulletin: we are actively monitoring a phishing campaign targeting staff with fake account alerts and payment requests. Please access your normal security dashboard to review indicators and report suspicious messages using the standard incident form.',
        explanation: 'Promotes secure behavior and points to standard internal reporting flow.',
        clues: ['Encourages reporting in official system', 'No request for private data'],
        safe: true,
      },
    ],
  },
]
