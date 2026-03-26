export type UserChoice = {
  id: string
  text: string
  nextMessageIndex: number
}

export type ChatMessage = {
  id: string
  speaker: 'contact' | 'user'
  text: string
  choices?: UserChoice[]
}

export type ChatScenario = {
  id: string
  title: string
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert'
  isPhishing: boolean
  persona: {
    name: string
    role: string
    company?: string
    relationship: string
  }
  context: string
  messages: ChatMessage[]
  redFlags: string[]
  goodSigns: string[]
  explanation: string
}

export const chatScenarios: ChatScenario[] = [
  // BEGINNER - Phishing
  {
    id: 'beginner-phishing-1',
    title: 'Urgent Account Verification',
    difficulty: 'Beginner',
    isPhishing: true,
    persona: {
      name: 'David Chen',
      role: 'Security Administrator',
      company: 'YourBank Corp',
      relationship: 'Customer support contact (new)'
    },
    context: 'You receive a message claiming to be from your bank security team',
    messages: [
      {
        id: 'm1',
        speaker: 'contact',
        text: 'Hi! This is David Chen from YourBank Security. We detected unusual activity on your account and need to verify your identity right now. Can you confirm your account number and PIN?'
      },
      {
        id: 'm2',
        speaker: 'user',
        text: '',
        choices: [
          {
            id: 'c1',
            text: 'Sure, here\'s my account info',
            nextMessageIndex: 2
          },
          {
            id: 'c2',
            text: 'That seems suspicious. I\'ll call the bank directly.',
            nextMessageIndex: 3
          }
        ]
      },
      {
        id: 'm3',
        speaker: 'contact',
        text: 'Great! Actually, I also need to send you a link to verify. It\'s https://yourbank-security-verify.click/account. Can you click it now?'
      },
      {
        id: 'm4',
        speaker: 'contact',
        text: 'No problem. Just so you know, we have your information here and will be monitoring for further suspicious activity.'
      }
    ],
    redFlags: [
      'Bank would never ask for PIN via chat or email',
      'Suspicious domain with ".click" TLD',
      'Pressure to act immediately',
      'Requesting sensitive information unsolicited'
    ],
    goodSigns: [],
    explanation:
      'Real banks never ask for account numbers or PINs through unsecured channels. The suspicious domain and immediate pressure are major red flags. Always verify by calling the official number on your card.'
  },

  // BEGINNER - Legitimate
  {
    id: 'beginner-legitimate-1',
    title: 'Team Project Update',
    difficulty: 'Beginner',
    isPhishing: false,
    persona: {
      name: 'Sarah Martinez',
      role: 'Project Manager',
      company: 'Your Company',
      relationship: 'Direct manager'
    },
    context: 'Your manager checks in about a project you\'re working on',
    messages: [
      {
        id: 'm1',
        speaker: 'contact',
        text: 'Hey! Just checking in on the Q2 project status. Do you have the latest updates to share?'
      },
      {
        id: 'm2',
        speaker: 'user',
        text: '',
        choices: [
          {
            id: 'c1',
            text: 'I\'ll send the status report shortly',
            nextMessageIndex: 2
          },
          {
            id: 'c2',
            text: 'Can you verify this is you before I share details?',
            nextMessageIndex: 3
          }
        ]
      },
      {
        id: 'm3',
        speaker: 'contact',
        text: 'Perfect! No rush. I just want to make sure we\'re on track for the demo next week. Share it when you\'re ready.'
      },
      {
        id: 'm4',
        speaker: 'contact',
        text: 'Of course! It\'s Sarah—check the internal directory or reach out through Teams if you need confirmation. Always good to verify.'
      }
    ],
    redFlags: [],
    goodSigns: [
      'Familiar internal context (Q2 project, demo)',
      'No request for credentials or sensitive data',
      'Respects your timeline, no artificial urgency',
      'Supports verification practices'
    ],
    explanation:
      'This is a normal work conversation with no suspicious requests. The manager respects your autonomy, provides context, and even encourages verification practices.'
  },

  // INTERMEDIATE - Phishing
  {
    id: 'intermediate-phishing-1',
    title: 'Vendor Payment Request',
    difficulty: 'Intermediate',
    isPhishing: true,
    persona: {
      name: 'Michael Thompson',
      role: 'Finance Manager',
      company: 'Acme Supplies Ltd',
      relationship: 'Regular vendor (contact changed)'
    },
    context: 'You receive a message from a regular vendor about payment details',
    messages: [
      {
        id: 'm1',
        speaker: 'contact',
        text: 'Hi there! Quick update: we\'ve migrated to a new banking system and all future payments should go to a new account. Can you update our details in your system?'
      },
      {
        id: 'm2',
        speaker: 'user',
        text: '',
        choices: [
          {
            id: 'c1',
            text: 'Sure, what\'s the new account info?',
            nextMessageIndex: 2
          },
          {
            id: 'c2',
            text: 'I\'ll verify this through official channels first',
            nextMessageIndex: 3
          }
        ]
      },
      {
        id: 'm3',
        speaker: 'contact',
        text: 'I\'ll send you a document with all the details. It should arrive in your email in a few minutes. Please process this ASAP—we have invoices coming due.'
      },
      {
        id: 'm4',
        speaker: 'contact',
        text: 'Sounds good. You can reach out to our accounting department on our official website if you need confirmation.'
      }
    ],
    redFlags: [
      'Unexpected change to payment details is a classic BEC tactic',
      'Pressure to update quickly without verification',
      'Unsolicited document attachment',
      'Mentions upcoming payment to increase urgency'
    ],
    goodSigns: [],
    explanation:
      'This is a Business Email Compromise (BEC) attack. Attackers often pose as vendors requesting payment changes. Always verify banking changes directly with the vendor using known contact numbers, not through the message.'
  },

  // INTERMEDIATE - Legitimate
  {
    id: 'intermediate-legitimate-1',
    title: 'Benefits Open Enrollment',
    difficulty: 'Intermediate',
    isPhishing: false,
    persona: {
      name: 'Jennifer Lo',
      role: 'HR Benefits Coordinator',
      company: 'Your Company',
      relationship: 'HR department (known contact)'
    },
    context: 'HR reminds you about benefits enrollment deadline',
    messages: [
      {
        id: 'm1',
        speaker: 'contact',
        text: 'Hi! Just a reminder that benefits open enrollment closes this Friday at 5 PM. Have you had a chance to review your options yet?'
      },
      {
        id: 'm2',
        speaker: 'user',
        text: '',
        choices: [
          {
            id: 'c1',
            text: 'Not yet, where do I go to enroll?',
            nextMessageIndex: 2
          },
          {
            id: 'c2',
            text: 'I\'ll handle it through the normal portal',
            nextMessageIndex: 3
          }
        ]
      },
      {
        id: 'm3',
        speaker: 'contact',
        text: 'You can access it through the employee portal on the company intranet—same place as last year. Let me know if you have questions about specific plans!'
      },
      {
        id: 'm4',
        speaker: 'contact',
        text: 'Great! If you need help understanding any of the plans, our HR team is available on the 3rd floor or you can email benefits@company.com.'
      }
    ],
    redFlags: [],
    goodSigns: [
      'Directs to official internal portal, no external links',
      'References established process ("same place as last year")',
      'Offers legitimate support channels',
      'No pressure for sensitive data'
    ],
    explanation:
      'Normal HR communication with proper guidance to official channels. Legitimate companies use established internal processes, not external links for sensitive operations.'
  },

  // ADVANCED - Phishing
  {
    id: 'advanced-phishing-1',
    title: 'Friend Account Recovery',
    difficulty: 'Advanced',
    isPhishing: true,
    persona: {
      name: 'Alex Kumar',
      role: 'Friend/Classmate',
      relationship: 'Close contact (account compromised)'
    },
    context: 'A trusted friend reaches out with an urgent problem',
    messages: [
      {
        id: 'm1',
        speaker: 'contact',
        text: 'Hey! I\'m in a really bad situation. My account got locked and support says they need someone I trust to verify my identity. Could you help me out? It would really mean a lot.'
      },
      {
        id: 'm2',
        speaker: 'user',
        text: '',
        choices: [
          {
            id: 'c1',
            text: 'Of course! What do you need me to do?',
            nextMessageIndex: 2
          },
          {
            id: 'c2',
            text: 'That sounds unusual. Is there another way to verify?',
            nextMessageIndex: 3
          }
        ]
      },
      {
        id: 'm3',
        speaker: 'contact',
        text: 'Thanks so much! I\'ll send you a link—you just need to sign in with your account and confirm that it\'s really me. Should only take 2 minutes.'
      },
      {
        id: 'm4',
        speaker: 'contact',
        text: 'Actually, that\'s a good point. You could try calling my phone directly to verify. My number is still the same.'
      }
    ],
    redFlags: [
      'Requests you sign in to verify someone else',
      'Uses emotional appeals and urgency ("really bad situation")',
      'Account compromise signs (requests from known contact)',
      'Asking to enter your credentials on unverified link'
    ],
    goodSigns: [],
    explanation:
      'This is account takeover impersonation. When a friend\'s account is compromised, attackers use their identity to harvest credentials from contacts. Never enter your login details on links sent through chat, even from trusted people. Call them directly instead.'
  },

  // ADVANCED - Legitimate
  {
    id: 'advanced-legitimate-1',
    title: 'IT System Maintenance',
    difficulty: 'Advanced',
    isPhishing: false,
    persona: {
      name: 'IT Services',
      role: 'Information Technology Department',
      company: 'Your Company',
      relationship: 'Internal IT support'
    },
    context: 'IT notifies you of scheduled system maintenance',
    messages: [
      {
        id: 'm1',
        speaker: 'contact',
        text: 'Heads up: we have scheduled maintenance tonight from 11 PM to 12:30 AM. Email and the portal will be briefly unavailable. No action needed from you.'
      },
      {
        id: 'm2',
        speaker: 'user',
        text: '',
        choices: [
          {
            id: 'c1',
            text: 'Got it, thanks for the notice',
            nextMessageIndex: 2
          },
          {
            id: 'c2',
            text: 'How do I access my account after maintenance?',
            nextMessageIndex: 3
          }
        ]
      },
      {
        id: 'm3',
        speaker: 'contact',
        text: 'You\'re welcome! We\'ll notify everyone when systems are back online.'
      },
      {
        id: 'm4',
        speaker: 'contact',
        text: 'Use your normal single sign-on process—nothing changes there. If you encounter any issues, reach out to the IT helpdesk at the usual number.'
      }
    ],
    redFlags: [],
    goodSigns: [
      'Provides specific maintenance window',
      'No requests for credentials or action from users',
      'References standard access methods',
      'Offers support channel for issues',
      'Informational only, no suspicious links'
    ],
    explanation:
      'Legitimate maintenance notice with clear information and no suspicious requests. Real IT departments inform users of maintenance windows and direct them to standard access methods.'
  },

  // EXPERT - Phishing
  {
    id: 'expert-phishing-1',
    title: 'Executive Wire Transfer',
    difficulty: 'Expert',
    isPhishing: true,
    persona: {
      name: 'James Wilson',
      role: 'CEO',
      company: 'Your Company',
      relationship: 'Executive leadership'
    },
    context: 'An urgent message that appears to be from the CEO',
    messages: [
      {
        id: 'm1',
        speaker: 'contact',
        text: 'Quick question—I need you to coordinate a confidential wire transfer for a strategic acquisition. Do NOT involve finance or your manager yet. This is sensitive.'
      },
      {
        id: 'm2',
        speaker: 'user',
        text: '',
        choices: [
          {
            id: 'c1',
            text: 'I\'ll handle it right away. How much?',
            nextMessageIndex: 2
          },
          {
            id: 'c2',
            text: 'I need to verify this with you directly',
            nextMessageIndex: 3
          }
        ]
      },
      {
        id: 'm3',
        speaker: 'contact',
        text: 'Good. Wire $250,000 to account 4521-0987-3456. I\'ll send you routing details. Reply when it\'s done. Speed is critical.'
      },
      {
        id: 'm4',
        speaker: 'contact',
        text: 'Fair point. Call my office and ask for my assistant to confirm. She\'s aware of this.'
      }
    ],
    redFlags: [
      'Requests secrecy and bypassing normal processes',
      'Authority impersonation (CEO)',
      'Large financial amount without proper authorization',
      'Pressure and urgency',
      'Asks not to involve appropriate departments'
    ],
    goodSigns: [],
    explanation:
      'Classic Business Email Compromise (CEO Fraud). High-risk indicators: authority, secrecy, financial request, and process bypass. Legitimate financial transfers always involve proper authorization and checks. Always verify by calling directly using a known number.'
  },

  // EXPERT - Legitimate
  {
    id: 'expert-legitimate-1',
    title: 'Security Training Requirement',
    difficulty: 'Expert',
    isPhishing: false,
    persona: {
      name: 'Information Security Team',
      role: 'Security Operations',
      company: 'Your Company',
      relationship: 'Internal security department'
    },
    context: 'Security team reminds you about mandatory training',
    messages: [
      {
        id: 'm1',
        speaker: 'contact',
        text: 'Reminder: please complete this month\'s mandatory security awareness training by Friday. Access it through your employee dashboard like you did last month.'
      },
      {
        id: 'm2',
        speaker: 'user',
        text: '',
        choices: [
          {
            id: 'c1',
            text: 'Where exactly is the training located?',
            nextMessageIndex: 2
          },
          {
            id: 'c2',
            text: 'I\'ll do it tonight',
            nextMessageIndex: 3
          }
        ]
      },
      {
        id: 'm3',
        speaker: 'contact',
        text: 'Log into the employee dashboard using your normal single sign-on, then go to Learning & Development. You can also contact our helpdesk if you have trouble accessing it.'
      },
      {
        id: 'm4',
        speaker: 'contact',
        text: 'Great, thanks! One more thing: remember, Security will NEVER ask for your password, 2FA code, or credentials through chat or email. Stay vigilant out there.'
      }
    ],
    redFlags: [],
    goodSigns: [
      'References established process ("like you did last month")',
      'Directs to standard single sign-on',
      'Clear legitimate support channel',
      'Explicitly states what they will never ask for',
      'Promotes good security practices'
    ],
    explanation:
      'Legitimate security communication with reinforced best practices. Notice how it explicitly states what legitimate security teams will never ask for, helping you identify phishing.'
  }
]
