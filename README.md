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

### 2) Immediate Feedback Loop

After each choice, the game gives:

- A short explanation
- A visual consequence (for example: account hacked, no incident, report success)

### 3) Branching Outcomes

Choices materially change progression:

- Good path: player remains secure
- Bad path: simulated compromise (identity theft, account takeover, data loss)

### 4) Difficulty Tiers

- Beginner: obvious phishing signals
- Intermediate: realistic and more subtle deception
- Advanced: targeted spear-phishing patterns

## Suggested Level Structure

### Level 1: Too Obvious

- Fake prize email
- Classic advance-fee style scam

### Level 2: Looks Real

- Bank security alert
- School portal credential prompt

### Level 3: Personalized Attack

- Message impersonating a friend
- Teacher or admin impersonation

### Level 4: Multi-Step Attack

- Initial email
- Fake login page
- Follow-up message that escalates pressure

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

## Demo
To see a demo of the game, please visit [PhishGuard Demo](https://serious-game-wine.vercel.app/) 