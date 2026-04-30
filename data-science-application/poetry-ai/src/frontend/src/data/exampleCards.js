/**
 * Example cards data for Poetry AI Assistant
 * Shows sample interactions and use cases
 */

export const exampleCards = [
  {
    id: 1,
    type: 'poet',
    icon: '�️',
    title: 'Poet Biography',
    query: 'Tell me about Sylvia Plath and her confessional poetry style',
    preview: 'Explore the life, struggles, and literary legacy of Sylvia Plath',
    response: 'Sylvia Plath (1932-1963) pioneered confessional poetry in works like "Ariel" and "The Bell Jar", candidly revealing her inner turmoil with vivid imagery.',
  },
  {
    id: 2,
    type: 'poem',
    icon: '🔍',
    title: 'Poem Analysis',
    query: 'Analyze the symbolism in "The Waste Land" by T.S. Eliot',
    preview: 'Uncover themes of spiritual desolation and postwar disillusionment',
    response: '"The Waste Land" (1922) uses fragmented imagery — the Thames, tarot cards, and the Fisher King myth — to portray the spiritual sterility of modern civilization after WWI.',
  },
  {
    id: 3,
    type: 'classification',
    icon: '🏷️',
    title: 'Poem Classification',
    query: 'Classify this poem for me',
    preview: 'Identify genre and style — try Shakespeare\'s Sonnet 18',
    poemExcerpt: 'Shall I compare thee to a summer\'s day?\nThou art more lovely and more temperate:\nRough winds do shake the darling buds of May,\nAnd summer\'s lease hath all too short a date.',
    response: 'Classification: Love Poetry | Style: Shakespearean Sonnet | Movement: Renaissance',
  },
  {
    id: 4,
    type: 'recommendation',
    icon: '💡',
    title: 'Poem Recommendations',
    query: 'Recommend poems similar to this one',
    preview: 'Discover poems similar to Frost\'s "The Road Not Taken"',
    poemExcerpt: 'Two roads diverged in a yellow wood,\nAnd sorry I could not travel both\nAnd be one traveler, long I stood\nAnd looked down one as far as I could\nTo where it bent in the undergrowth;',
    response: 'Recommended: "Stopping by Woods on a Snowy Evening" by Frost, "The Journey" by Mary Oliver, "Invictus" by Henley',
  },
  {
    id: 5,
    type: 'poet',
    icon: '📚',
    title: 'Poet Influence',
    query: 'What was Walt Whitman\'s influence on modern American poetry?',
    preview: 'Discover how Whitman\'s free verse in "Leaves of Grass" shaped poetry',
    response: 'Walt Whitman\'s free verse in "Leaves of Grass" (1855) broke metrical conventions and celebrated democratic individualism, deeply influencing Langston Hughes, Allen Ginsberg, and Pablo Neruda.',
  },
  {
    id: 6,
    type: 'poem',
    icon: '💭',
    title: 'Theme Analysis',
    query: 'What is the theme of "Do Not Go Gentle Into That Good Night" by Dylan Thomas?',
    preview: 'Explore Dylan Thomas\'s defiant elegy written for his dying father',
    response: 'The villanelle uses the dual refrains "Do not go gentle" and "Rage, rage against the dying of the light" to embody fierce resistance against mortality, grief, and the love between father and son.',
  },
];

export const sampleConversations = [
  {
    id: 1,
    title: 'Understanding Romantic Poetry',
    messages: [
      {
        role: 'user',
        content: 'Who was Lord Byron and what was his significance?',
        timestamp: new Date(Date.now() - 300000),
      },
      {
        role: 'bot',
        content: 'Lord Byron (1788-1824) was a British Romantic poet and a major figure in 19th-century literature. He was known for his dramatic, passionate poetry and his tumultuous personal life. His most famous works include "She Walks in Beauty" and "Don Juan."',
        timestamp: new Date(Date.now() - 280000),
      },
      {
        role: 'user',
        content: 'Can you classify this poem I wrote?',
        timestamp: new Date(Date.now() - 200000),
      },
      {
        role: 'system',
        content: 'Please provide poem text for classification',
        timestamp: new Date(Date.now() - 190000),
      },
    ],
  },
  {
    id: 2,
    title: 'Modern Poetry Exploration',
    messages: [
      {
        role: 'user',
        content: 'Who is Mary Oliver?',
        timestamp: new Date(Date.now() - 600000),
      },
      {
        role: 'bot',
        content: 'Mary Oliver (1935-2019) was an American poet known for her accessible, spiritual poetry about nature. Her most famous poem is "The Journey," exploring themes of self-discovery and authenticity. She won the Pulitzer Prize for Poetry in 1984.',
        timestamp: new Date(Date.now() - 580000),
      },
    ],
  },
];

export const poetryTerms = [
  {
    term: 'Sonnet',
    definition: 'A 14-line poem with a specific rhyme scheme, often about love or beauty',
    example: 'Shakespeare\'s sonnets',
  },
  {
    term: 'Haiku',
    definition: 'A three-line poem with 5-7-5 syllable structure, often about nature',
    example: 'Traditional Japanese form',
  },
  {
    term: 'Metaphor',
    definition: 'A figure of speech comparing two unlike things without using "like" or "as"',
    example: '"Love is a journey"',
  },
  {
    term: 'Alliteration',
    definition: 'The repetition of initial consonant sounds in neighboring words',
    example: '"Silently slipping through silver streams"',
  },
  {
    term: 'Iambic Pentameter',
    definition: 'A metrical pattern with 10 syllables per line in alternating stressed/unstressed beats',
    example: 'Commonly used by Shakespeare',
  },
];
