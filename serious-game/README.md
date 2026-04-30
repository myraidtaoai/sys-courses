# PhishGuard: Interactive Phishing Awareness Game

PhishGuard is a scenario-driven serious game that trains players to recognize and respond to phishing attacks under realistic pressure.

Instead of a simple quiz, the experience is designed as a choose-your-path interactive story where decisions create immediate consequences.

## Core Game Concept

- The player takes a role such as student, intern, gamer, or influencer.
- The game delivers suspicious communications through chat-style messages: emails, texts, and DMs.
- The player chooses an action in each situation.
- Each choice branches to a good or bad outcome.
- The game explains why the action was safe or risky.

## Learning Objectives

Players should learn to detect and respond to:

- Suspicious links
- Fake urgency (for example: "ACT NOW")
- Spoofed sender addresses
- Too-good-to-be-true offers
- Requests for sensitive information

## Game Mechanics

### 1) Scenario-Based Conversations

Each level is a scenario with realistic context.

Example:

- Message: "Your Netflix account is suspended. Verify now."
- Player options:
  - Click link immediately
  - Check sender email
  - Ignore
  - Report as phishing

### 2) AI-Driven Chat Simulation (NEW)

The app now includes an interactive "AI Chat Drill" mode where:

- Users chat with an AI-controlled contact whose true nature is unknown
- Each persona is randomly either a **genuine colleague/manager/customer** or a **phishing attacker**
- The conversation unfolds through 3-4 message exchanges with branching user choices
- After the dialogue, users must make a judgment: **Trust & Continue** or **Report as Phishing**
- Each drill includes 3 randomized scenarios drawn from 8 pre-scripted conversations
- Results show detailed explanations with red flags (for phishing) or good signs (for legitimate)

**Why this works:**
- Users cannot predict the scenario outcome based on name or title alone
- Dialogue reveals clues progressively, teaching pattern recognition
- Multi-turn format mirrors real social engineering attempts
- Judgment phase forces active decision-making, not passive reading

### 3) Immediate Feedback Loop

After each choice, the game gives:

- A short explanation
- A visual consequence (for example: account hacked, no incident, report success)

### 4) Branching Outcomes

Choices materially change progression:

- Good path: player remains secure
- Bad path: simulated compromise (identity theft, account takeover, data loss)

- Beginner: obvious phishing signals, fake prizes, classic scams
- Intermediate: realistic scenarios, mixed signals, vendor impersonation
- Advanced: personalized and contextual lures, impersonation of trusted contacts
- Expert: advanced BEC (Business Email Compromise), CEO fraud, legal hold threats

## Gameplay Modes

### Traditional Message Review

Choose from 4 difficulty levels (Beginner, Intermediate, Advanced, Expert). Each level presents a series of message scenarios presented in a mobile-style interface. Players classify each message as "Safe" or "Phishing" and receive feedback.

### AI Chat Drill

Engage in live conversations with randomized personas. The system randomly selects a character to be either:

- ✅ **Legitimate**: A genuine colleague, manager, customer, or partner
- 🚨 **Phishing Attacker**: Impersonating a legitimate contact or authority

Without knowing which, players must:

1. Read the persona and context
2. Engage in 3-4 message exchanges with branching dialogue choices
3. Make a final judgment: Trust the contact or Report as Phishing
4. View detailed analysis explaining clues, red flags, or good security practices

**8 Pre-Scripted Scenarios:**

- Beginner: Bank account verification scam vs. normal team update
- Intermediate: Vendor payment fraud vs. HR benefits enrollment
- Advanced: Friend account recovery impersonation vs. IT maintenance notice
- Expert: CEO wire fraud vs. security training reminder

## Differentiator: Conversational UX

PhishGuard focuses on emotional realism, not static Q and A.

Real attacks exploit urgency, confusion, and social pressure. The chat-style interface recreates those conditions so players practice good decisions in context.

## Gamification

- Security Awareness Score
- Phish Meter indicating risk exposure
- Badge progression:
  - Link Detective
  - Spoof Buster
- Optional timer rounds for high-pressure scenarios

## Product Direction

### MVP (Current Direction)

- Frontend: React 19 + TypeScript
- Styling: Tailwind CSS 4 with custom theming and Inter typography
- Icons: Lucide React
- Animation: Motion
- UI pattern: chat-like message flow with branching decisions

### Future Enhancement

- Dynamic scenario generation with OpenAI API
- Reduced predictability for replayability
- More adaptive and realistic phishing simulations

## What To Avoid

Do not reduce the game to a binary quiz.

Bad approach:

- "Is this phishing? Yes or No"

Good approach:

- Place the player inside realistic pressure and ambiguity
- Make consequences visible and memorable

## Local Development

### Prerequisites

- Node.js 20+
- npm 10+

### Run

```bash
npm install
npm run dev
```

Then open the local URL shown in terminal (usually `http://localhost:5173`).

### Quality Checks

```bash
npm run lint
npm run build
```

## Online Demo
To see a demo of the game, please visit [PhishGuard Demo](https://serious-game-wine.vercel.app/) 